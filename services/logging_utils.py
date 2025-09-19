from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List


def write_checkpoint(seed: int, provider: str, persona: str, prompts: List[str], outputs: List[str]) -> Path:
    """Persist a minimal checkpoint JSON for reproducibility.

    Writes to directory pointed by NSPLLM_LOG_DIR env var or `./.nspllm_logs`.
    Returns the path to the created file.
    """
    root = Path(os.getenv("NSPLLM_LOG_DIR", ".nspllm_logs"))
    root.mkdir(parents=True, exist_ok=True)
    target = root / "checkpoint.json"
    payload: Dict[str, Any] = {
        "seed": seed,
        "provider": provider,
        "persona": persona,
        "prompts": prompts,
        "outputs": outputs,
    }
    target.write_text(json.dumps(payload))
    return target
