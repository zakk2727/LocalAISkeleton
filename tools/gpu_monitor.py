import subprocess
import psutil
import docker
import json
from typing import Dict, Any

def get_vram_usage() -> Dict[str, Any]:
    """
    Collects VRAM usage via nvidia-smi, system memory via psutil, 
    and active containers via the Docker SDK.
    """
    stats = {
        "gpu_info": {},
        "system_info": {},
        "docker_info": []
    }

    # 1. Fetch NVIDIA VRAM Info
    try:
        # Querying name, total memory, and used memory
        cmd = "nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounit"
        output = subprocess.check_output(cmd.split()).decode('utf-8').strip()
        lines = output.split('\n')
        
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 3:
                stats["gpu_info"].append({
                    "name": parts[0].strip(),
                    "total_mb": int(parts[1].strip()),
                    "used_mb": int(parts[2].strip())
                })
    except Exception as e:
        stats["gpu_error"] = f"nvidia-smi failed: {str(e)}"

    # 2. Fetch System RAM Info
    mem = psutil.virtual_memory()
    stats["system_info"] = {
        "total_mb": mem.total // (1024 * 1024),
        "used_mb": mem.used // (1024 * 1024),
        "percent": mem.percent
    }

    # 3. Fetch Docker Container Info
    try:
        # Attempting connection via the standard socket; 
        # if remote/bridged, it can be passed via base_url
        client = docker.DockerClient(from_env=True)
        containers = client.containers.list()
        for container in containers:
            stats["docker_info"].append({
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown"
            })
    except Exception as e:
        stats["docker_error"] = f"Docker SDK failed: {str(e)}"

    return stats

if __name__ == "__main__":
    # Simple CLI test for the tool
    print(json.dumps(get_vram_usage(), indent=2))
