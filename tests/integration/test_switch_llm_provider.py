import importlib


def test_switch_llm_provider_via_config(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    cfg = importlib.import_module("services.config")
    assert hasattr(cfg, "build_services")
    services = cfg.build_services()
    assert isinstance(services, dict)
    # Expect wiring to provide llm_repo instance of the mock provider
    repo = services.get("llm_repo")
    assert repo is not None, "build_services() must return {'llm_repo': ...} when LLM_PROVIDER=mock"
    from repositories.implementations.mock_llm_repo import MockLLMRepository

    assert isinstance(repo, MockLLMRepository), "LLM provider must switch to MockLLMRepository when LLM_PROVIDER=mock"
