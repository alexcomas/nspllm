import json
import logging
import requests
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from global_methods import find_filenames, check_if_file_exists

logger = logging.getLogger(__name__)

# Configuration - adjust these based on your setup
SIM_SERVER_URL = "http://localhost:9000"  # Where reverie.py serves

def health_check(request):
    """Check health of both environment and simulation servers"""
    env_server = True  # Django is responding
    sim_server = False
    
    try:
        # Try to ping the simulation server
        response = requests.get(f"{SIM_SERVER_URL}/health", timeout=5)
        sim_server = response.status_code == 200
    except Exception as e:
        logger.warning(f"Simulation server health check failed: {e}")
    
    return JsonResponse({
        "env_server": env_server,
        "sim_server": sim_server,
        "timestamp": datetime.now().isoformat()
    })

def simulations_list(request):
    """List all simulations or create a new one"""
    if request.method == 'GET':
        simulations = []
        
        # Check storage directory for simulations
        storage_path = "storage"
        if os.path.exists(storage_path):
            for sim_name in os.listdir(storage_path):
                sim_path = os.path.join(storage_path, sim_name)
                if os.path.isdir(sim_path):
                    # Get simulation metadata
                    meta_file = os.path.join("compressed_storage", sim_name, "meta.json")
                    
                    # Check if this is a completed simulation with meta
                    if os.path.exists(meta_file):
                        try:
                            with open(meta_file, 'r') as f:
                                meta = json.load(f)
                            
                            simulations.append({
                                "id": sim_name,
                                "name": sim_name.replace("_", " ").title(),
                                "base_id": meta.get("fork_sim_code", "unknown"),
                                "status": "completed",
                                "created_at": datetime.now().isoformat(),
                                "current_step": meta.get("step", 0),
                                "total_steps": meta.get("step", 0)
                            })
                        except Exception as e:
                            logger.warning(f"Failed to read meta for {sim_name}: {e}")
                    else:
                        # This is likely an active/base simulation
                        # Check for environment files to determine current step
                        env_path = os.path.join(sim_path, "environment")
                        current_step = 0
                        
                        if os.path.exists(env_path):
                            try:
                                env_files = find_filenames(env_path, ".json")
                                if env_files:
                                    steps = [int(os.path.basename(f).split('.')[0]) for f in env_files]
                                    current_step = max(steps) if steps else 0
                            except Exception as e:
                                logger.warning(f"Failed to determine step for {sim_name}: {e}")
                        
                        # Determine status based on temp files
                        status = "paused"
                        if check_if_file_exists("temp_storage/curr_sim_code.json"):
                            try:
                                with open("temp_storage/curr_sim_code.json", 'r') as f:
                                    curr_sim = json.load(f)
                                if curr_sim.get("sim_code") == sim_name:
                                    status = "running" if check_if_file_exists("temp_storage/curr_step.json") else "paused"
                            except:
                                pass
                        
                        simulations.append({
                            "id": sim_name,
                            "name": sim_name.replace("_", " ").title(),
                            "base_id": "base" if sim_name.startswith("base_") else "unknown",
                            "status": status,
                            "created_at": datetime.now().isoformat(),
                            "current_step": current_step,
                            "total_steps": None
                        })
        
        # List all simulation forks/steps individually (no grouping)
        # Sort by current step descending (most recent first)
        simulations.sort(key=lambda x: x["current_step"] if x["current_step"] is not None else 0, reverse=True)
        return JsonResponse(simulations, safe=False)
    
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
        # First, try to get from compressed storage (completed simulation)
        meta_file = os.path.join("compressed_storage", sim_id, "meta.json")
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                meta = json.load(f)
            
            # Get the latest movement data
            movement_file = os.path.join("compressed_storage", sim_id, "master_movement.json")
            if os.path.exists(movement_file):
                with open(movement_file, 'r') as f:
                    movement_data = json.load(f)
                
                # Get the last step
                last_step = str(meta["step"])
                if last_step in movement_data:
                    agents = []
                    for persona_name, persona_data in movement_data[last_step].items():
                        # Get persona details from persona files
                        persona_path = os.path.join("compressed_storage", sim_id, "personas", persona_name)
                        description = "A generative agent"
                        
                        if os.path.exists(persona_path):
                            desc_file = os.path.join(persona_path, "bootstrap_memory", "associative_memory", "embeddings.json")
                            if os.path.exists(desc_file):
                                try:
                                    with open(desc_file, 'r') as f:
                                        embed_data = json.load(f)
                                    # Get the description from the first entry
                                    if embed_data and len(embed_data) > 0:
                                        first_key = list(embed_data.keys())[0]
                                        description = embed_data[first_key].get("description", description)
                                except:
                                    pass
                        
                        agents.append({
                            "id": persona_name.replace(" ", "_"),
                            "name": persona_name,
                            "persona": description,
                            "location": {
                                "x": persona_data["movement"][0],
                                "y": persona_data["movement"][1], 
                                "area": persona_data.get("description", "Unknown area")
                            },
                            "current_action": persona_data.get("description", "No current action"),
                            "emotions": {
                                "happiness": 0.7,
                                "curiosity": 0.8,
                                "energy": 0.6
                            }
                        })
                    
                    return JsonResponse({
                        "step": meta["step"],
                        "agents": agents,
                        "environment": {
                            "time": meta["curr_time"],
                            "weather": "Clear",
                            "events": [f"Simulation completed at step {meta['step']}"]
                        }
                    })
        
        # If not in compressed storage, check active simulation
        sim_path = os.path.join("storage", sim_id)
        if os.path.exists(sim_path):
            # Get current environment state
            env_path = os.path.join(sim_path, "environment")
            if os.path.exists(env_path):
                # Find the latest environment file
                env_files = find_filenames(env_path, ".json")
                if env_files:
                    steps = [(int(os.path.basename(f).split('.')[0]), f) for f in env_files]
                    steps.sort(reverse=True)
                    latest_step, latest_file = steps[0]
                    
                    with open(latest_file, 'r') as f:
                        env_data = json.load(f)
                    
                    agents = []
                    for persona_name, persona_pos in env_data.items():
                        # Try to get persona description
                        persona_path = os.path.join(sim_path, "personas", persona_name)
                        description = "A generative agent"
                        
                        if os.path.exists(persona_path):
                            # Try to read persona description from memory
                            desc_files = find_filenames(persona_path, ".json")
                            for desc_file in desc_files:
                                if "bootstrap_memory" in desc_file:
                                    try:
                                        with open(desc_file, 'r') as f:
                                            desc_data = json.load(f)
                                        if isinstance(desc_data, dict) and "description" in desc_data:
                                            description = desc_data["description"]
                                            break
                                    except:
                                        continue
                        
                        agents.append({
                            "id": persona_name.replace(" ", "_"),
                            "name": persona_name,
                            "persona": description,
                            "location": {
                                "x": persona_pos["x"],
                                "y": persona_pos["y"],
                                "area": persona_pos.get("maze", "Unknown area")
                            },
                            "current_action": "Exploring the environment",
                            "emotions": {
                                "happiness": 0.7,
                                "curiosity": 0.8,
                                "energy": 0.6
                            }
                        })
                    
                    return JsonResponse({
                        "step": latest_step,
                        "agents": agents,
                        "environment": {
                            "time": datetime.now().strftime("%B %d, %Y, %H:%M:%S"),
                            "weather": "Clear",
                            "events": [f"Active simulation at step {latest_step}"]
                        }
                    })
        
        # Fallback to mock data if simulation not found
        return JsonResponse({
            "step": 0,
            "agents": [],
            "environment": {
                "time": datetime.now().strftime("%B %d, %Y, %H:%M:%S"),
                "weather": "Clear",
                "events": [f"Simulation {sim_id} not found"]
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get simulation state {sim_id}: {e}")
        return JsonResponse({
            "step": 0,
            "agents": [],
            "environment": {
                "time": datetime.now().strftime("%B %d, %Y, %H:%M:%S"),
                "weather": "Clear",
                "events": [f"Error loading simulation: {str(e)}"]
            }
        })

def get_replay(request, replay_id):
    """Get replay data by ID"""
    try:
        # Look for replay in compressed storage
        meta_file = os.path.join("compressed_storage", replay_id, "meta.json")
        movement_file = os.path.join("compressed_storage", replay_id, "master_movement.json")
        
        if os.path.exists(meta_file) and os.path.exists(movement_file):
            # Load metadata
            with open(meta_file, 'r') as f:
                meta = json.load(f)
            
            # Load movement data
            with open(movement_file, 'r') as f:
                movement_data = json.load(f)
            
            frames = []
            persona_names = meta["persona_names"]
            
            # Convert movement data to frames (sample every 10 steps for performance)
            step_keys = sorted([int(k) for k in movement_data.keys()])
            sample_steps = step_keys[::10] if len(step_keys) > 100 else step_keys  # Sample for large datasets
            
            for step in sample_steps:
                step_str = str(step)
                if step_str in movement_data:
                    agents = []
                    step_data = movement_data[step_str]
                    
                    for persona_name in persona_names:
                        if persona_name in step_data:
                            persona_data = step_data[persona_name]
                            
                            # Get persona description
                            description = "A generative agent"
                            persona_path = os.path.join("compressed_storage", replay_id, "personas", persona_name)
                            if os.path.exists(persona_path):
                                desc_file = os.path.join(persona_path, "bootstrap_memory", "associative_memory", "embeddings.json")
                                if os.path.exists(desc_file):
                                    try:
                                        with open(desc_file, 'r') as f:
                                            embed_data = json.load(f)
                                        if embed_data and len(embed_data) > 0:
                                            first_key = list(embed_data.keys())[0]
                                            description = embed_data[first_key].get("description", description)
                                    except:
                                        pass
                            
                            agents.append({
                                "id": persona_name.replace(" ", "_"),
                                "name": persona_name,
                                "persona": description,
                                "location": {
                                    "x": persona_data["movement"][0],
                                    "y": persona_data["movement"][1],
                                    "area": persona_data.get("description", "Unknown area")
                                },
                                "current_action": persona_data.get("description", "Moving around"),
                                "emotions": {
                                    "happiness": 0.7,
                                    "curiosity": 0.8,
                                    "energy": 0.6
                                }
                            })
                    
                    # Calculate timestamp based on start date and step
                    start_date = datetime.strptime(meta["start_date"] + " 00:00:00", "%B %d, %Y %H:%M:%S")
                    current_time = start_date
                    for i in range(step):
                        current_time = current_time.replace(second=current_time.second + meta["sec_per_step"])
                        if current_time.second >= 60:
                            current_time = current_time.replace(minute=current_time.minute + 1, second=current_time.second - 60)
                        if current_time.minute >= 60:
                            current_time = current_time.replace(hour=current_time.hour + 1, minute=current_time.minute - 60)
                        if current_time.hour >= 24:
                            current_time = current_time.replace(day=current_time.day + 1, hour=current_time.hour - 24)
                    
                    frames.append({
                        "step": step,
                        "timestamp": current_time.isoformat(),
                        "agents": agents,
                        "events": [f"Step {step} completed"] if step % 100 == 0 else []
                    })
            
            # Calculate total duration
            total_duration = meta["step"] * meta["sec_per_step"]
            
            return JsonResponse({
                "id": replay_id,
                "simulation_id": replay_id,
                "name": f"Replay: {replay_id}",
                "frames": frames,
                "metadata": {
                    "total_steps": meta["step"],
                    "duration_seconds": total_duration,
                    "agent_count": len(persona_names)
                }
            })
        
        # If not found in compressed storage, try active/in-progress simulation in storage/{sim_id}/environment/*.json
        env_path = os.path.join("storage", replay_id, "environment")
        if os.path.exists(env_path):
            env_files = find_filenames(env_path, ".json")
            if env_files:
                # Sort by frame number
                steps = sorted([(int(os.path.basename(f).split('.')[0]), f) for f in env_files])
                frames = []
                persona_names = set()
                for step, file_path in steps:
                    with open(file_path, 'r') as f:
                        env_data = json.load(f)
                    agents = []
                    for persona_name, persona_pos in env_data.items():
                        persona_names.add(persona_name)
                        # Remove 'the_ville' as area if present, otherwise show area or blank
                        area = persona_pos.get("maze", "")
                        if area == "the_ville":
                            area = ""
                        # Try to get a more specific action if available
                        action = persona_pos.get("current_action") or persona_pos.get("description") or ""
                        if not action or action == "the_ville":
                            action = "Exploring the environment"
                        agents.append({
                            "id": persona_name.replace(" ", "_"),
                            "name": persona_name,
                            "persona": "A generative agent",
                            "location": {
                                "x": persona_pos["x"],
                                "y": persona_pos["y"],
                                "area": area
                            },
                            "current_action": action,
                            "emotions": {
                                "happiness": 0.7,
                                "curiosity": 0.8,
                                "energy": 0.6
                            }
                        })
                    frames.append({
                        "step": step,
                        "timestamp": datetime.now().isoformat(),
                        "agents": agents,
                        "events": [f"Step {step} completed"] if step % 100 == 0 else []
                    })
                return JsonResponse({
                    "id": replay_id,
                    "simulation_id": replay_id,
                    "name": f"Replay: {replay_id}",
                    "frames": frames,
                    "metadata": {
                        "total_steps": len(frames),
                        "duration_seconds": len(frames) * 10,  # Unknown sec_per_step, default 10
                        "agent_count": len(persona_names)
                    }
                })
        
        # Fallback to mock data if replay not found
        return JsonResponse({
            "id": replay_id,
            "simulation_id": replay_id,
            "name": f"Replay {replay_id} (Not Found)",
            "frames": [
                {
                    "step": 1,
                    "timestamp": datetime.now().isoformat(),
                    "agents": [],
                    "events": [f"Replay {replay_id} not found in storage"]
                }
            ],
            "metadata": {
                "total_steps": 1,
                "duration_seconds": 10,
                "agent_count": 0
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to load replay {replay_id}: {e}")
        return JsonResponse({
            "id": replay_id,
            "simulation_id": replay_id,
            "name": f"Replay {replay_id} (Error)",
            "frames": [
                {
                    "step": 1,
                    "timestamp": datetime.now().isoformat(),
                    "agents": [],
                    "events": [f"Error loading replay: {str(e)}"]
                }
            ],
            "metadata": {
                "total_steps": 1,
                "duration_seconds": 10,
                "agent_count": 0
            }
        })