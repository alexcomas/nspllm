import json
import os
from pathlib import Path

from services.logging_utils import write_checkpoint


def test_reproducible_logging(tmp_path, test_seed, log_dir):
    os.environ["TEST_SEED"] = str(test_seed)
    ckpt = write_checkpoint(test_seed, "mock", "test", ["hello"], ["world"])

    # Expectations
    assert ckpt.exists(), "Checkpoint must be created"
    payload = json.loads(ckpt.read_text())
    assert payload.get("seed") == test_seed
    assert "prompts" in payload and isinstance(payload["prompts"], list)
    assert "outputs" in payload and isinstance(payload["outputs"], list)
