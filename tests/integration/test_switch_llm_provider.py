import importlib


def test_switch_llm_provider_via_config(monkeypatch):
    # Mock path
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    cfg = importlib.import_module("services.config")
    assert hasattr(cfg, "build_services")
    services = cfg.build_services()
    assert isinstance(services, dict)
    repo = services.get("llm_repo")
    assert repo is not None, "build_services() must return {'llm_repo': ...} when LLM_PROVIDER=mock"
    from repositories.implementations.mock_llm_repo import MockLLMRepository

    assert isinstance(repo, MockLLMRepository)

    # OpenAI path (no network calls here, just instance type)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key")
    importlib.reload(cfg)
    services2 = cfg.build_services()
    repo2 = services2.get("llm_repo")
    assert repo2 is not None, "build_services() must return {'llm_repo': OpenAIRepo} when LLM_PROVIDER=openai and OPENAI_API_KEY set"
    from repositories.implementations.openai_repo import OpenAIRepo

    assert isinstance(repo2, OpenAIRepo)
