import types

from services.implementations.planning_service_shim import PlanningServiceShim
from repositories.implementations.mock_llm_repo import MockLLMRepository
from services.environment_service import EnvironmentService


class _Persona:
    def __init__(self):
        class _Scratch:
            def __init__(self):
                self._finished = True
                self.act_address = (1, 2)

            def act_check_finished(self):
                return self._finished

        self.scratch = _Scratch()
        self.name = "Unit"


def test_planning_service_delegates(monkeypatch):
    # Arrange: monkeypatch legacy planner to ensure delegation is called
    target_result = (9, 9)

    def fake_legacy_plan(persona, maze, personas, new_day, retrieved):
        assert persona.name == "Unit"
        return target_result

    # Inject a fake legacy module to avoid importing heavy dependencies
    import sys
    import types as _types
    legacy = _types.ModuleType("reverie.backend_server.persona.cognitive_modules.plan")
    legacy.plan = fake_legacy_plan
    monkeypatch.setitem(
        sys.modules,
        "reverie.backend_server.persona.cognitive_modules.plan",
        legacy,
    )

    # Minimal DI setup
    llm = MockLLMRepository()

    class DummyEnvService(EnvironmentService):
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

    env = DummyEnvService()

    svc = PlanningServiceShim(llm, env)

    # Act
    out = svc.plan(_Persona(), maze=types.SimpleNamespace(), personas={}, new_day=False, retrieved={})

    # Assert
    assert out == target_result
