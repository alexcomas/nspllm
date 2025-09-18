import importlib


def test_planning_module_interface_exports():
    mod = importlib.import_module("services.planning_service")
    assert hasattr(mod, "PlanningModule"), "Expect `PlanningModule` exported from services.planning_service"
    pm = getattr(mod, "PlanningModule")
    assert hasattr(pm, "plan"), "`PlanningModule` must define `plan(...)`"
    assert hasattr(pm, "replan"), "`PlanningModule` must define `replan(...)`"
    assert hasattr(pm, "next_action"), "`PlanningModule` must define `next_action(...)`"


def test_planning_module_error_type_present():
    mod = importlib.import_module("services.planning_service")
    assert hasattr(mod, "PlanningError"), "Expect domain-specific `PlanningError` exported"
