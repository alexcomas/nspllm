from services.implementations.dialogue_service_shim import DialogueServiceShim
from repositories.implementations.mock_llm_repo import MockLLMRepository
from services.environment_service import EnvironmentService


def test_dialogue_service_next_utterance_monkeypatched(monkeypatch):
    # Inject a fake legacy converse function to avoid heavy imports
    import sys, types

    mod = types.ModuleType("reverie.backend_server.persona.cognitive_modules.converse")

    def fake_agent_chat_v1(maze, init_persona, target_persona):
        return ["A: hi", "B: hey"]

    mod.agent_chat_v1 = fake_agent_chat_v1
    monkeypatch.setitem(sys.modules, "reverie.backend_server.persona.cognitive_modules.converse", mod)

    class DummyEnv(EnvironmentService):
        def read_environment_step(self, sim_code, step):
            raise NotImplementedError

        def write_movement_step(self, sim_code, step, movements):
            raise NotImplementedError

        def read_meta(self, sim_code):
            raise NotImplementedError

        def write_meta(self, sim_code, meta):
            raise NotImplementedError

        def signal_curr_sim(self, sim_code, step):
            raise NotImplementedError

    svc = DialogueServiceShim(MockLLMRepository(), DummyEnv())

    class P:
        def __init__(self, name):
            self.name = name

    out = svc.next_utterance(P("A"), P("B"), {"maze": object()})
    assert out == "A: hi\nB: hey"
