import json
import logging
import requests
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# Configuration - adjust these based on your setup
SIM_SERVER_URL = "http://localhost:9000"  # Where reverie.py serves

def health_check(request):
    """Check health of both environment and simulation servers"""
    env_server = True  # Django is responding
    sim_server = True  # For development, assume simulation is available
    
    # TODO: Implement actual simulation server health check when HTTP wrapper is ready
    # try:
    #     # Try to ping the simulation server
    #     response = requests.get(f"{SIM_SERVER_URL}/health", timeout=5)
    #     sim_server = response.status_code == 200
    # except Exception as e:
    #     logger.warning(f"Simulation server health check failed: {e}")
    
    return JsonResponse({
        "env_server": env_server,
        "sim_server": sim_server,
        "timestamp": datetime.now().isoformat()
    })

def simulations_list(request):
    """List all simulations or create a new one"""
    if request.method == 'GET':
        # TODO: Implement actual simulation listing
        # For now, return mock data
        return JsonResponse([
            {
                "id": "demo_001",
                "name": "Demo Simulation",
                "base_id": "demo",
                "status": "completed",
                "created_at": "2025-09-12T10:00:00Z",
                "current_step": 100,
                "total_steps": 100
            }
        ], safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        base_id = data.get('base_id', 'demo')
        
        # TODO: Create actual simulation via reverie.py
        # For now, return mock created simulation
        sim_id = f"{base_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return JsonResponse({
            "id": sim_id,
            "name": f"{base_id.title()} Simulation",
            "base_id": base_id,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "current_step": 0,
            "total_steps": None
        })

@csrf_exempt
@require_http_methods(["POST"])
def run_simulation(request, sim_id):
    """Run simulation for specified steps"""
    data = json.loads(request.body)
    steps = data.get('steps', 1)
    
    try:
        # Proxy to simulation server
        response = requests.post(
            f"{SIM_SERVER_URL}/simulations/{sim_id}/run",
            json={"steps": steps},
            timeout=30
        )
        
        if response.status_code == 200:
            return JsonResponse({"success": True, "steps": steps})
        else:
            return JsonResponse(
                {"error": "Simulation server error", "details": response.text},
                status=response.status_code
            )
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to run simulation {sim_id}: {e}")
        return JsonResponse(
            {"error": "Failed to connect to simulation server"},
            status=503
        )

@csrf_exempt
@require_http_methods(["POST"])
def pause_simulation(request, sim_id):
    """Pause a running simulation"""
    try:
        response = requests.post(f"{SIM_SERVER_URL}/simulations/{sim_id}/pause", timeout=10)
        return JsonResponse({"success": True})
    except Exception as e:
        logger.error(f"Failed to pause simulation {sim_id}: {e}")
        return JsonResponse({"error": str(e)}, status=503)

def simulation_state(request, sim_id):
    """Get current state of simulation"""
    try:
        response = requests.get(f"{SIM_SERVER_URL}/simulations/{sim_id}/state", timeout=10)
        return JsonResponse(response.json())
    except Exception as e:
        logger.error(f"Failed to get simulation state {sim_id}: {e}")
        # Return mock state for development
        return JsonResponse({
            "step": 42,
            "agents": [
                {
                    "id": "agent_001",
                    "name": "Alice",
                    "persona": "A friendly researcher",
                    "location": {"x": 10, "y": 20, "area": "library"},
                    "current_action": "Reading a book",
                    "emotions": {"happiness": 0.7, "curiosity": 0.8}
                }
            ],
            "environment": {
                "time": "2025-09-12T14:30:00Z",
                "weather": "sunny",
                "events": ["Library opened", "New book arrived"]
            }
        })

def get_replay(request, replay_id):
    """Get replay data by ID"""
    # TODO: Implement actual replay loading from storage
    # For now, return mock replay data
    return JsonResponse({
        "id": replay_id,
        "simulation_id": "demo_001",
        "name": f"Replay {replay_id}",
        "frames": [
            {
                "step": 1,
                "timestamp": "2025-09-12T14:00:00Z",
                "agents": [
                    {
                        "id": "agent_001",
                        "name": "Alice",
                        "persona": "A friendly researcher",
                        "location": {"x": 5, "y": 10, "area": "entrance"},
                        "current_action": "Entering library",
                        "emotions": {"happiness": 0.6, "curiosity": 0.9}
                    }
                ],
                "events": ["Simulation started"]
            }
        ],
        "metadata": {
            "total_steps": 100,
            "duration_seconds": 300,
            "agent_count": 1
        }
    })