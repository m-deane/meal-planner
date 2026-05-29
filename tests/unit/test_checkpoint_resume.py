"""
Tests for checkpoint behaviour that underpins a correct scraper resume:
- create_session must copy the URL list (so iteration is not perturbed)
- failures keep the session incomplete (so they are not silently discarded)
"""

from src.utils.checkpoint import CheckpointManager


def test_create_session_copies_url_list(tmp_path):
    manager = CheckpointManager(checkpoint_file=tmp_path / "cp.json")
    urls = ["https://example.com/a", "https://example.com/b", "https://example.com/c"]

    manager.create_session("s1", urls)

    # Marking success must not mutate the caller's original list.
    manager.mark_success(urls[0], auto_save=False)
    assert urls == ["https://example.com/a", "https://example.com/b", "https://example.com/c"]
    assert len(manager.data.pending_urls) == 2


def test_session_not_complete_while_failures_remain(tmp_path):
    manager = CheckpointManager(checkpoint_file=tmp_path / "cp.json")
    urls = ["https://example.com/a", "https://example.com/b"]
    manager.create_session("s2", urls)

    manager.mark_success("https://example.com/a", auto_save=False)
    manager.mark_failure("https://example.com/b", auto_save=False)

    # Pending is empty but a failure remains -> NOT complete (so it isn't cleared).
    assert len(manager.data.pending_urls) == 0
    assert manager.is_complete() is False

    # Once the failure is resolved, the session is complete.
    manager.data.failed_urls.discard("https://example.com/b")
    assert manager.is_complete() is True


def test_no_urls_skipped_when_marking_during_iteration(tmp_path):
    """Reproduces the resume corruption: iterating pending_urls while marking
    must visit every URL exactly once."""
    manager = CheckpointManager(checkpoint_file=tmp_path / "cp.json")
    urls = [f"https://example.com/{i}" for i in range(10)]
    manager.create_session("s3", urls)

    visited = []
    for url in list(manager.data.pending_urls):
        visited.append(url)
        manager.mark_success(url, auto_save=False)

    assert visited == urls
    assert len(manager.data.pending_urls) == 0
