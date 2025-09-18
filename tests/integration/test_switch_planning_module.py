import importlib


def test_switch_planning_module(monkeypatch):
    monkeypatch.setenv("PLAN_MODULE", "shim")
    cfg = importlib.import_module("services.config")
    assert hasattr(cfg, "build_services")
    services = cfg.build_services()
    assert isinstance(services, dict)

    svc = services.get("planning_service")
    assert svc is not None, "build_services() must include 'planning_service' when PLAN_MODULE=shim"

    from services.implementations.planning_service_shim import PlanningServiceShim

    assert isinstance(svc, PlanningServiceShim), "Planning module must switch to PlanningServiceShim when PLAN_MODULE=shim"
