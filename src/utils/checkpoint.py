"""
Checkpoint/resume functionality for long-running scraping operations.
Tracks progress and allows resumption from failures.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from src.config import config
from src.utils.logger import get_logger

logger = get_logger("checkpoint")


class CheckpointData(BaseModel):
    """Checkpoint state model."""

    session_id: str = Field(description="Unique session identifier")
    started_at: datetime = Field(description="Session start time")
    last_updated: datetime = Field(description="Last checkpoint update time")
    total_urls: int = Field(ge=0, description="Total URLs to process")
    processed_urls: Set[str] = Field(default_factory=set, description="Successfully processed URLs")
    failed_urls: Set[str] = Field(default_factory=set, description="Failed URLs")
    pending_urls: List[str] = Field(default_factory=list, description="URLs yet to process")
    success_count: int = Field(ge=0, default=0, description="Number of successful scrapes")
    failure_count: int = Field(ge=0, default=0, description="Number of failed scrapes")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            set: lambda v: list(v)
        }


class CheckpointManager:
    """Manages scraping checkpoints for resume functionality."""

    def __init__(self, checkpoint_file: Optional[Path] = None):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_file: Path to checkpoint file (uses config default if None)
        """
        self.checkpoint_file = checkpoint_file or Path(config.checkpoint_file)
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.data: Optional[CheckpointData] = None
        self.auto_save_counter = 0

    def create_session(
        self,
        session_id: str,
        urls: List[str],
        metadata: Optional[Dict[str, str]] = None
    ) -> CheckpointData:
        """
        Create new checkpoint session.

        Args:
            session_id: Unique session identifier
            urls: List of URLs to process
            metadata: Optional session metadata

        Returns:
            CheckpointData instance
        """
        self.data = CheckpointData(
            session_id=session_id,
            started_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            total_urls=len(urls),
            pending_urls=urls,
            metadata=metadata or {}
        )

        self.save()
        logger.info(
            f"Created checkpoint session: {session_id} | "
            f"Total URLs: {len(urls)}"
        )

        return self.data

    def load(self) -> Optional[CheckpointData]:
        """
        Load checkpoint from file.

        Returns:
            CheckpointData if file exists, None otherwise
        """
        if not self.checkpoint_file.exists():
            logger.debug("No checkpoint file found")
            return None

        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)

            data_dict['processed_urls'] = set(data_dict.get('processed_urls', []))
            data_dict['failed_urls'] = set(data_dict.get('failed_urls', []))
            data_dict['started_at'] = datetime.fromisoformat(data_dict['started_at'])
            data_dict['last_updated'] = datetime.fromisoformat(data_dict['last_updated'])

            self.data = CheckpointData(**data_dict)

            logger.info(
                f"Loaded checkpoint: {self.data.session_id} | "
                f"Processed: {len(self.data.processed_urls)} | "
                f"Pending: {len(self.data.pending_urls)} | "
                f"Failed: {len(self.data.failed_urls)}"
            )

            return self.data

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}", exc_info=True)
            return None

    def save(self) -> None:
        """Save checkpoint to file."""
        if not self.data:
            logger.warning("No checkpoint data to save")
            return

        self.data.last_updated = datetime.utcnow()

        try:
            checkpoint_dict = self.data.model_dump()
            checkpoint_dict['processed_urls'] = list(self.data.processed_urls)
            checkpoint_dict['failed_urls'] = list(self.data.failed_urls)
            checkpoint_dict['started_at'] = self.data.started_at.isoformat()
            checkpoint_dict['last_updated'] = self.data.last_updated.isoformat()

            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_dict, f, indent=2, ensure_ascii=False)

            logger.debug(f"Checkpoint saved: {self.checkpoint_file}")

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}", exc_info=True)

    def mark_success(self, url: str, auto_save: bool = True) -> None:
        """
        Mark URL as successfully processed.

        Args:
            url: URL that was successfully processed
            auto_save: Automatically save checkpoint
        """
        if not self.data:
            return

        self.data.processed_urls.add(url)
        self.data.success_count += 1

        if url in self.data.pending_urls:
            self.data.pending_urls.remove(url)

        if url in self.data.failed_urls:
            self.data.failed_urls.remove(url)

        if auto_save:
            self._auto_save()

    def mark_failure(self, url: str, auto_save: bool = True) -> None:
        """
        Mark URL as failed.

        Args:
            url: URL that failed to process
            auto_save: Automatically save checkpoint
        """
        if not self.data:
            return

        self.data.failed_urls.add(url)
        self.data.failure_count += 1

        if url in self.data.pending_urls:
            self.data.pending_urls.remove(url)

        if auto_save:
            self._auto_save()

    def get_next_url(self) -> Optional[str]:
        """
        Get next URL to process.

        Returns:
            Next URL or None if no URLs remaining
        """
        if not self.data or not self.data.pending_urls:
            return None

        return self.data.pending_urls[0]

    def get_progress(self) -> Dict[str, int]:
        """
        Get current progress statistics.

        Returns:
            Dictionary with progress metrics
        """
        if not self.data:
            return {
                'total': 0,
                'processed': 0,
                'pending': 0,
                'failed': 0,
                'success': 0,
                'percentage': 0.0
            }

        processed = len(self.data.processed_urls)
        total = self.data.total_urls
        percentage = (processed / total * 100) if total > 0 else 0

        return {
            'total': total,
            'processed': processed,
            'pending': len(self.data.pending_urls),
            'failed': len(self.data.failed_urls),
            'success': self.data.success_count,
            'percentage': round(percentage, 2)
        }

    def _auto_save(self) -> None:
        """Auto-save checkpoint based on interval."""
        if not config.checkpoint_enabled:
            return

        self.auto_save_counter += 1

        if self.auto_save_counter >= config.checkpoint_interval:
            self.save()
            self.auto_save_counter = 0

    def clear(self) -> None:
        """Clear checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            logger.info("Checkpoint cleared")

        self.data = None
        self.auto_save_counter = 0

    def is_complete(self) -> bool:
        """
        Check if session is complete.

        Returns:
            True if all URLs processed or failed
        """
        if not self.data:
            return True

        return len(self.data.pending_urls) == 0

    def get_session_duration(self) -> Optional[float]:
        """
        Get session duration in seconds.

        Returns:
            Duration in seconds or None if no session
        """
        if not self.data:
            return None

        return (datetime.utcnow() - self.data.started_at).total_seconds()


def create_checkpoint_manager(
    checkpoint_file: Optional[Path] = None
) -> CheckpointManager:
    """
    Factory function to create checkpoint manager.

    Args:
        checkpoint_file: Optional custom checkpoint file path

    Returns:
        CheckpointManager instance
    """
    return CheckpointManager(checkpoint_file)
