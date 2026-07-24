import os
from pydantic import BaseModel, Field


class TrueContainerMetrics(BaseModel):
    memory_usage_percent: float = Field(
        ..., description="Memory usage Percentage of this container"
    )
    memory_used_gb: float = Field(
        ..., description="Memory used in Gigabytes of this container"
    )


def get_true_container_memory() -> dict:
    """Reads Linux cgroups to get the exact memory metrics of THIS container."""
    try:
        # 1. Read exact memory currently used by this container (in bytes)
        with open("/sys/fs/cgroup/memory/memory.usage_in_bytes", "r") as f:
            used_bytes = int(f.read().strip())

        # 2. Read the maximum memory limit allowed for this container
        with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
            limit_bytes = int(f.read().strip())

        # Fallback safeguard if no memory limit was explicitly set in docker-compose
        # (Linux sets the limit to a massive sub-system number if uncapped)
        if limit_bytes > 9223372036854771712:
            # Fall back to host system total RAM if uncapped
            import psutil

            limit_bytes = psutil.virtual_memory().total

        # 3. Calculate true isolated container variables
        used_gb = round(used_bytes / (1024**3), 2)
        usage_percent = round((used_bytes / limit_bytes) * 100, 1)

        return {"memory_usage_percent": usage_percent, "memory_used_gb": used_gb}
    except FileNotFoundError:
        # Fallback path if testing natively on a Windows/Mac host machine outside Docker cgroups
        import psutil

        vm = psutil.virtual_memory()
        return {
            "memory_usage_percent": vm.percent,
            "memory_used_gb": round(vm.used / (1024**3), 2),
        }


if __name__ == "__main__":
    metrics = get_true_container_memory()
    print(metrics)
