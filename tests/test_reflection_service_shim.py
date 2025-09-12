from services.implementations.reflection_service_shim import ReflectionServiceShim


def test_reflection_service_delegates(monkeypatch):
    # Inject fake legacy reflect module
    import sys, types

    mod = types.ModuleType("reverie.backend_server.persona.cognitive_modules.reflect")

    called = {"count": 0}

    def fake_run_reflect(persona):
        called["count"] += 1

    mod.run_reflect = fake_run_reflect
    monkeypatch.setitem(sys.modules, "reverie.backend_server.persona.cognitive_modules.reflect", mod)

    svc = ReflectionServiceShim()

    class P: pass

    svc.reflect(P())
    assert called["count"] == 1
