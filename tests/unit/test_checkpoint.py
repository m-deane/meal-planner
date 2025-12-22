"""
Unit tests for checkpoint module.
Tests checkpoint/resume functionality for scraping operations.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from src.utils.checkpoint import CheckpointData, CheckpointManager, create_checkpoint_manager


class TestCheckpointData:
    """Test CheckpointData model."""

    def test_initialization(self):
        """Test CheckpointData initialization."""
        data = CheckpointData(
            session_id='test_session',
            started_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            total_urls=10
        )

        assert data.session_id == 'test_session'
        assert data.total_urls == 10
        assert data.success_count == 0
        assert data.failure_count == 0
        assert len(data.processed_urls) == 0
        assert len(data.failed_urls) == 0
        assert len(data.pending_urls) == 0

    def test_model_validation(self):
        """Test model validation."""
        with pytest.raises(Exception):
            CheckpointData(
                session_id='test',
                started_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                total_urls=-1
            )


class TestCheckpointManager:
    """Test CheckpointManager class."""

    def test_initialization(self, temp_checkpoint_file):
        """Test manager initialization."""
        manager = CheckpointManager(checkpoint_file=temp_checkpoint_file)

        assert manager.checkpoint_file == temp_checkpoint_file
        assert manager.data is None
        assert manager.auto_save_counter == 0

    def test_create_session(self, checkpoint_manager):
        """Test creating new checkpoint session."""
        urls = ['url1', 'url2', 'url3']
        metadata = {'key': 'value'}

        data = checkpoint_manager.create_session(
            session_id='test_session',
            urls=urls,
            metadata=metadata
        )

        assert data.session_id == 'test_session'
        assert data.total_urls == 3
        assert len(data.pending_urls) == 3
        assert data.metadata == metadata

    def test_save_and_load(self, checkpoint_manager, temp_checkpoint_file):
        """Test saving and loading checkpoint."""
        urls = ['url1', 'url2']
        checkpoint_manager.create_session('test_session', urls)

        assert temp_checkpoint_file.exists()

        new_manager = CheckpointManager(checkpoint_file=temp_checkpoint_file)
        loaded_data = new_manager.load()

        assert loaded_data is not None
        assert loaded_data.session_id == 'test_session'
        assert loaded_data.total_urls == 2
        assert len(loaded_data.pending_urls) == 2

    def test_load_nonexistent_checkpoint(self, checkpoint_manager):
        """Test loading when no checkpoint exists."""
        result = checkpoint_manager.load()

        assert result is None

    def test_mark_success(self, checkpoint_manager):
        """Test marking URL as successful."""
        urls = ['url1', 'url2', 'url3']
        checkpoint_manager.create_session('test', urls)

        checkpoint_manager.mark_success('url1', auto_save=False)

        assert 'url1' in checkpoint_manager.data.processed_urls
        assert 'url1' not in checkpoint_manager.data.pending_urls
        assert checkpoint_manager.data.success_count == 1

    def test_mark_failure(self, checkpoint_manager):
        """Test marking URL as failed."""
        urls = ['url1', 'url2', 'url3']
        checkpoint_manager.create_session('test', urls)

        checkpoint_manager.mark_failure('url1', auto_save=False)

        assert 'url1' in checkpoint_manager.data.failed_urls
        assert 'url1' not in checkpoint_manager.data.pending_urls
        assert checkpoint_manager.data.failure_count == 1

    def test_mark_success_removes_from_failed(self, checkpoint_manager):
        """Test marking success removes URL from failed set."""
        urls = ['url1']
        checkpoint_manager.create_session('test', urls)

        checkpoint_manager.mark_failure('url1', auto_save=False)
        checkpoint_manager.mark_success('url1', auto_save=False)

        assert 'url1' in checkpoint_manager.data.processed_urls
        assert 'url1' not in checkpoint_manager.data.failed_urls

    def test_get_next_url(self, checkpoint_manager):
        """Test getting next URL to process."""
        urls = ['url1', 'url2', 'url3']
        checkpoint_manager.create_session('test', urls)

        next_url = checkpoint_manager.get_next_url()

        assert next_url == 'url1'

    def test_get_next_url_empty(self, checkpoint_manager):
        """Test getting next URL when queue is empty."""
        checkpoint_manager.create_session('test', [])

        next_url = checkpoint_manager.get_next_url()

        assert next_url is None

    def test_get_progress(self, checkpoint_manager):
        """Test getting progress statistics."""
        urls = ['url1', 'url2', 'url3', 'url4']
        checkpoint_manager.create_session('test', urls)

        checkpoint_manager.mark_success('url1', auto_save=False)
        checkpoint_manager.mark_success('url2', auto_save=False)
        checkpoint_manager.mark_failure('url3', auto_save=False)

        progress = checkpoint_manager.get_progress()

        assert progress['total'] == 4
        assert progress['processed'] == 2
        assert progress['pending'] == 1
        assert progress['failed'] == 1
        assert progress['success'] == 2
        assert progress['percentage'] == 50.0

    def test_get_progress_no_data(self, checkpoint_manager):
        """Test progress when no checkpoint data."""
        progress = checkpoint_manager.get_progress()

        assert progress['total'] == 0
        assert progress['percentage'] == 0.0

    def test_auto_save(self, checkpoint_manager, test_config):
        """Test auto-save functionality."""
        test_config.checkpoint_enabled = True
        test_config.checkpoint_interval = 2

        urls = ['url1', 'url2', 'url3']
        checkpoint_manager.create_session('test', urls)

        checkpoint_manager.mark_success('url1', auto_save=True)
        assert checkpoint_manager.auto_save_counter == 1

        checkpoint_manager.mark_success('url2', auto_save=True)
        assert checkpoint_manager.auto_save_counter == 0

    def test_clear_checkpoint(self, checkpoint_manager, temp_checkpoint_file):
        """Test clearing checkpoint file."""
        checkpoint_manager.create_session('test', ['url1'])

        assert temp_checkpoint_file.exists()

        checkpoint_manager.clear()

        assert not temp_checkpoint_file.exists()
        assert checkpoint_manager.data is None

    def test_is_complete_true(self, checkpoint_manager):
        """Test session completion check when complete."""
        checkpoint_manager.create_session('test', ['url1'])
        checkpoint_manager.mark_success('url1', auto_save=False)

        assert checkpoint_manager.is_complete() is True

    def test_is_complete_false(self, checkpoint_manager):
        """Test session completion check when incomplete."""
        checkpoint_manager.create_session('test', ['url1', 'url2'])
        checkpoint_manager.mark_success('url1', auto_save=False)

        assert checkpoint_manager.is_complete() is False

    def test_is_complete_no_data(self, checkpoint_manager):
        """Test session completion check with no data."""
        assert checkpoint_manager.is_complete() is True

    def test_get_session_duration(self, checkpoint_manager):
        """Test getting session duration."""
        checkpoint_manager.create_session('test', ['url1'])

        duration = checkpoint_manager.get_session_duration()

        assert duration is not None
        assert duration >= 0

    def test_get_session_duration_no_data(self, checkpoint_manager):
        """Test session duration with no data."""
        duration = checkpoint_manager.get_session_duration()

        assert duration is None

    def test_save_without_data(self, checkpoint_manager):
        """Test saving when no data exists."""
        checkpoint_manager.save()

    def test_checkpoint_persistence(self, temp_checkpoint_file):
        """Test checkpoint persists across manager instances."""
        urls = ['url1', 'url2', 'url3']

        manager1 = CheckpointManager(checkpoint_file=temp_checkpoint_file)
        manager1.create_session('test', urls)
        manager1.mark_success('url1', auto_save=False)
        manager1.save()

        manager2 = CheckpointManager(checkpoint_file=temp_checkpoint_file)
        data = manager2.load()

        assert data.total_urls == 3
        assert 'url1' in data.processed_urls
        assert len(data.pending_urls) == 2


def test_create_checkpoint_manager():
    """Test factory function creates manager."""
    manager = create_checkpoint_manager()

    assert isinstance(manager, CheckpointManager)
