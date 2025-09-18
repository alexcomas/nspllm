import importlib


def test_llm_repository_contract_methods_present():
    mod = importlib.import_module("repositories.llm_repository")
    assert hasattr(mod, "LLMRepository"), "Expect `LLMRepository` exported from repositories.llm_repository"
    repo = getattr(mod, "LLMRepository")
    # Contract requires these high-level methods; implementations may down-map to chat
    assert hasattr(repo, "generate"), "`LLMRepository` must define generate(prompt: str, **kwargs)"
    assert hasattr(repo, "structured"), "`LLMRepository` must define structured(prompt: str, schema: dict, **kwargs)"
    assert hasattr(repo, "call_function"), "`LLMRepository` must define call_function(prompt: str, functions: list[dict], **kwargs)"
