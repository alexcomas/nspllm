import os
import sys
from pathlib import Path
import random
from typing import Iterator

import pytest


def _add_project_root_to_syspath() -> None:
    # tests/ -> project root
    root = Path(__file__).resolve().parents[1]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


_add_project_root_to_syspath()


@pytest.fixture()
def test_seed(monkeypatch: pytest.MonkeyPatch) -> int:
    """Provide and apply a deterministic seed for tests that request it.

    Usage in tests:
        def test_something(test_seed):
            ...

    Reads optional env var TEST_SEED; defaults to 1234.
    Applies to Python's random; attempts NumPy if available; sets PYTHONHASHSEED.
    """
    seed_str = os.getenv("TEST_SEED", "1234")
    try:
        seed = int(seed_str)
    except ValueError:
        seed = 1234

    random.seed(seed)
    try:
        import numpy as np  # type: ignore

        np.random.seed(seed)
    except Exception:
        pass

    monkeypatch.setenv("PYTHONHASHSEED", str(seed))
    return seed


@pytest.fixture()
def log_dir(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated logs directory and expose it via env var for tests.

    Sets NSPLLM_LOG_DIR so code can discover where to persist logs/checkpoints.
    """
    path = tmp_path_factory.mktemp("logs")
    monkeypatch.setenv("NSPLLM_LOG_DIR", str(path))
    return path
