from __future__ import annotations

import os
from typing import Any, Dict

from repositories.implementations.mock_llm_repo import MockLLMRepository
from repositories.implementations.openai_repo import OpenAIRepo
from repositories.implementations.file_env_repo import FileEnvRepo
from services.implementations.environment_service_fs import FileSystemEnvironmentService
from services.implementations.planning_service_shim import PlanningServiceShim
from repositories.environment_repository import EnvironmentRepository

# Placeholder wiring helpers. Concrete factories will be provided during Phase 5.

def build_services(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    plan_module = os.getenv("PLAN_MODULE", "shim").lower()

    # LLM repo selection
    if llm_provider == "mock":
        llm_repo = MockLLMRepository()
    else:
        # Defer actual API usage; if OPENAI_API_KEY not set, tests should avoid initializing.
        # Use a dummy client pattern in unit tests; here we construct only when key present.
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            llm_repo = OpenAIRepo(api_key=api_key)
        else:
            # Fall back to mock to make test environment deterministic without secrets
            llm_repo = MockLLMRepository()

    # Environment service wiring (filesystem-based paths can be overridden later)
    env_repo = FileEnvRepo()
    storage_root = os.getenv("NSPLLM_STORAGE_ROOT", "environment/frontend_server/storage")
    temp_root = os.getenv("NSPLLM_TEMP_ROOT", "environment/temp_storage")
    env_service = FileSystemEnvironmentService(env_repo, storage_root, temp_root)

    services: Dict[str, Any] = {"llm_repo": llm_repo, "environment_service": env_service}

    # Planning module selection
    if plan_module == "shim":
        services["planning_service"] = PlanningServiceShim(llm_repo, env_service)

    return services
