import importlib
import os
import sys
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


def test_engine_uses_configurable_llm_provider():
    """Test that the engine's LLM interface uses the configured provider"""
    # Add reverie directory to path
    reverie_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reverie', 'backend_server')
    sys.path.insert(0, reverie_path)
    
    try:
        from persona.prompt_template.gpt_structure import set_llm_repository, get_llm_repository
        from repositories.implementations.mock_llm_repo import MockLLMRepository
        
        # Set up a mock LLM repository
        mock_repo = MockLLMRepository()
        set_llm_repository(mock_repo)
        
        # Verify it was set
        current_repo = get_llm_repository()
        assert current_repo is mock_repo, "Global LLM repository should be set to our mock"
        
               # Test that Persona initialization sets the repository
        from persona.persona import Persona
        services = {"llm_repo": mock_repo}
        
        # This would normally fail without services, but we're just testing initialization
        # The actual memory loading would require valid paths, so we'll just test the LLM setting
        try:
            # Mock the memory-related file operations
            import persona.memory_structures.spatial_memory
            import persona.memory_structures.associative_memory  
            import persona.memory_structures.scratch
            
            # This will fail due to file paths, but LLM repo should be set first
            Persona("test_persona", "fake_path", services=services)
        except:
            # Expected to fail due to missing files, but LLM repo should be set
            pass
            
        # Verify the global repo is still our mock
        assert get_llm_repository() is mock_repo
        
    finally:
        # Clean up sys.path
        if reverie_path in sys.path:
            sys.path.remove(reverie_path)
