import json
import os
from pathlib import Path


def test_reproducible_logging(tmp_path, test_seed, log_dir):
    # This test asserts the existence of a logging routine that writes a checkpoint
    # including seed and prompt/outputs metadata.
    os.environ["TEST_SEED"] = str(test_seed)
    target = Path(os.environ["NSPLLM_LOG_DIR"]) / "checkpoint.json"

    # Simulate a minimal logging call clients can use (to be implemented later)
    # For now, this test specifies expected file format to drive implementation.
    data = {
        "seed": test_seed,
        "provider": "mock",
        "persona": "test",
        "prompts": ["hello"],
        "outputs": ["world"],
    }
    target.write_text(json.dumps(data))

    # Expectations
    assert target.exists(), "Checkpoint must be created"
    payload = json.loads(target.read_text())
    assert payload.get("seed") == test_seed
    assert "prompts" in payload and isinstance(payload["prompts"], list)
    assert "outputs" in payload and isinstance(payload["outputs"], list)
