"""Stage timers separate wall-clock from CPU time and count child processes."""

import subprocess
import sys
import time

from logique.benchmarks.timing import Stage, load_average, machine, peak_memory


def test_waiting_costs_wall_clock_but_no_cpu():
    with Stage() as stage:
        time.sleep(0.2)
    assert stage.wall_s >= 0.2
    assert stage.cpu_s < 0.1


def test_busy_work_costs_cpu():
    with Stage() as stage:
        total = 0
        for i in range(2_000_000):
            total += i * i
    assert stage.cpu_s > 0.02
    assert stage.child_cpu_s == 0


def test_a_child_process_counts_toward_the_stage():
    busy = "s = 0\nfor i in range(3_000_000):\n    s += i * i"
    with Stage() as stage:
        subprocess.run([sys.executable, "-c", busy], check=True)
    assert stage.child_cpu_s > 0.05
    assert stage.cpu_s >= stage.child_cpu_s


def test_records_use_the_study_names():
    with Stage() as stage:
        pass
    assert set(stage.record("schedule")) == {"schedule_s", "schedule_cpu_s"}


def test_machine_memory_and_load_are_recorded():
    record = machine()
    assert record["logical_cores"] >= 1 and record["system"]
    assert record["memory_bytes"] is None or record["memory_bytes"] > 2**28
    memory = peak_memory()
    assert memory["peak_rss_bytes"] > 2**20  # this interpreter uses over 1 MB
    load = load_average()
    assert load is None or load >= 0
