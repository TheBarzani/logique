"""Stage timing, memory and machine records for compilation-time studies.

Each stage records wall-clock time and CPU time. CPU time is the primary measure
on a shared machine: wall-clock time also counts the time a process waits for a
core. The CPU time of a stage includes the child processes it waited for, such
as the native bridge, which runs as a subprocess.

Peak resident memory comes from ``getrusage``, which reports the maximum over
the life of the process (and, for children, over all children waited for so
far), so it bounds a case from above when several cases share one process;
a per-case peak requires running each case in its own process.
"""

from dataclasses import dataclass
import os
import platform
import resource
import subprocess
import sys
import time


def _children_cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


@dataclass
class Stage:
    """Wall-clock and CPU seconds of one stage, filled when the block exits."""

    wall_s: float = 0.0
    cpu_s: float = 0.0
    child_cpu_s: float = 0.0

    def __enter__(self):
        self._wall = time.perf_counter()
        self._cpu = time.process_time()
        self._child = _children_cpu()
        return self

    def __exit__(self, *exc):
        self.wall_s = time.perf_counter() - self._wall
        self.child_cpu_s = _children_cpu() - self._child
        self.cpu_s = time.process_time() - self._cpu + self.child_cpu_s
        return False

    def record(self, name: str) -> dict:
        """The stage as ``<name>_s`` (wall-clock) and ``<name>_cpu_s`` (CPU)."""
        return {f"{name}_s": self.wall_s, f"{name}_cpu_s": self.cpu_s}


def _bytes(maxrss: int) -> int:
    # Linux reports kilobytes, macOS bytes.
    return maxrss if sys.platform == "darwin" else maxrss * 1024


def peak_memory() -> dict:
    """Peak resident memory of this process and of its largest child so far."""
    return {
        "peak_rss_bytes": _bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "children_peak_rss_bytes": _bytes(
            resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        ),
    }


def load_average() -> float | None:
    """One-minute load average, or None where the platform has none."""
    try:
        return os.getloadavg()[0]
    except OSError:
        return None


def _sysctl(name: str) -> str | None:
    try:
        return subprocess.check_output(
            ["sysctl", "-n", name], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def machine() -> dict:
    """Processor, core counts, memory and operating system of this machine."""
    record = {
        "system": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "logical_cores": os.cpu_count(),
        "processor": platform.processor() or None,
        "memory_bytes": None,
    }
    if sys.platform == "darwin":
        record["processor"] = _sysctl("machdep.cpu.brand_string") or record["processor"]
        memory = _sysctl("hw.memsize")
        record["memory_bytes"] = int(memory) if memory else None
        # Apple silicon: performance and efficiency cores run at different speeds.
        for level, label in ((0, "performance_cores"), (1, "efficiency_cores")):
            value = _sysctl(f"hw.perflevel{level}.physicalcpu")
            if value:
                record[label] = int(value)
    else:
        try:
            pages, size = os.sysconf("SC_PHYS_PAGES"), os.sysconf("SC_PAGE_SIZE")
            record["memory_bytes"] = pages * size
        except (ValueError, OSError, AttributeError):
            pass
    return record
