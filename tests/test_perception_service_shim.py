from services.implementations.perception_service_shim import PerceptionServiceShim


def test_perception_service_delegates(monkeypatch):
    # Monkeypatch legacy perceive to avoid heavy imports
    import sys, types

    mod = types.ModuleType("reverie.backend_server.persona.cognitive_modules.perceive")

    def fake_perceive(persona, maze):
        return ["event1", "event2"]

    mod.perceive = fake_perceive
    monkeypatch.setitem(sys.modules, "reverie.backend_server.persona.cognitive_modules.perceive", mod)

    svc = PerceptionServiceShim()

    class P: pass
    class M: pass

    out = svc.perceive(P(), M())
    assert out == ["event1", "event2"]
