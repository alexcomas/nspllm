import importlib
from unittest.mock import MagicMock


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


def test_planning_service_interface_available():
    """Test that the planning service implements the expected interface"""
    cfg = importlib.import_module("services.config")
    services = cfg.build_services()
    planning_service = services.get("planning_service")
    
    # Verify the service has the expected interface methods
    assert hasattr(planning_service, "plan"), "Planning service must have 'plan' method"
    
    # Verify it's the correct type
    from services.implementations.planning_service_shim import PlanningServiceShim
    assert isinstance(planning_service, PlanningServiceShim)
    
    # This demonstrates that engine code can call planning_service.plan() 
    # without needing to know which specific planning module is selected
