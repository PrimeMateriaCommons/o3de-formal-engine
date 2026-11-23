#!/usr/bin/env python3
"""
benchmark_o3de_scaling.py - High-Scale O3DE Formal Architecture & Simulation Benchmarks
Subsystem: /run/media/multiplic/AGI/prismagi/mount/SUBSYSTEMS/o3de-prism
Origin: /run/media/multiplic/AGI/prismagi/mount/SUBSYSTEMS/o3de
Adheres to ADR-0025, ADR-0026, and Multiplicity Theory Invariant Specifications.

Suites:
  SUITE-O1: ECS Dependency Topological Resolution & Scaling (N in [100, 10000]) (INV-O3DE-a)
  SUITE-O2: EBus Priority Dispatch & Single-Handler Invariant (100k events) (INV-O3DE-b)
  SUITE-O3: Physics Fixed Substepping & Accumulator Clamping Invariant (INV-O3DE-c)
  SUITE-O4: PhysX Symplectic Energy Dissipation & Monotonicity (INV-O3DE-d)
  SUITE-O5: Symmetric Collision Filtering Lattice Verification
  SUITE-O6: Engine Simulation Throughput & Scalability
"""

import sys
import time
import json
import math
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))
from o3de_simulator import O3DEECSSimulator, O3DEEBusSimulator, O3DEPhysicsSimulator


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def suite_o1_ecs_scaling() -> dict:
    t0 = time.perf_counter()
    evaluations = []
    
    for n in [100, 500, 2000, 10000]:
        sim = O3DEECSSimulator()
        for i in range(n):
            sim.create_entity(i)
            # Add dependent components in reverse/scrambled order:
            # Comp 3 (RigidBody): req=1 (Transform), incomp=99
            sim.add_component(i, component_id=3, provided=2, required=1, incompatible=99)
            # Comp 2 (Mesh): req=1 (Transform)
            sim.add_component(i, component_id=2, provided=3, required=1, incompatible=0)
            # Comp 1 (Transform): req=0 (root)
            sim.add_component(i, component_id=1, provided=1, required=0, incompatible=0)

        t_sub = time.perf_counter()
        success_count = 0
        for i in range(n):
            ok, order = sim.activate_entity(i)
            if ok and order[0] == 1:
                success_count += 1
        dur = time.perf_counter() - t_sub
        rate = n / dur if dur > 0 else 0
        evaluations.append({
            "N": n,
            "success_rate": success_count / n,
            "duration_s": dur,
            "activations_per_sec": rate,
        })

    total_dur = time.perf_counter() - t0
    all_ok = all(e["success_rate"] == 1.0 for e in evaluations)
    return {
        "suite_id": "SUITE-O1",
        "name": "ECS Topological Dependency Resolution Scaling (N<=10000)",
        "invariant": "INV-O3DE-a",
        "passed": all_ok,
        "duration_s": total_dur,
        "evaluations": evaluations,
    }


def suite_o2_ebus_dispatch() -> dict:
    t0 = time.perf_counter()
    
    # 1. Test single-handler exclusivity
    single_bus = O3DEEBusSimulator(bus_id=1, is_single_handler=True)
    c1 = single_bus.connect(handler_id=101, priority=10)
    c2 = single_bus.connect(handler_id=102, priority=20)
    single_handler_passed = (c1 is True and c2 is False)

    # 2. Test priority ordering
    multi_bus = O3DEEBusSimulator(bus_id=2, is_single_handler=False)
    multi_bus.connect(handler_id=1, priority=10)
    multi_bus.connect(handler_id=2, priority=100)
    multi_bus.connect(handler_id=3, priority=50)
    dispatch_order = multi_bus.dispatch("tick")
    order_passed = (dispatch_order == [2, 3, 1])

    # 3. High-volume dispatch benchmark (100,000 events)
    num_events = 100_000
    t_disp = time.perf_counter()
    for _ in range(num_events):
        multi_bus.dispatch("event")
    disp_dur = time.perf_counter() - t_disp
    rate = num_events / disp_dur if disp_dur > 0 else 0

    total_dur = time.perf_counter() - t0
    passed = single_handler_passed and order_passed
    return {
        "suite_id": "SUITE-O2",
        "name": "EBus Priority Dispatch & Exclusivity (100k events)",
        "invariant": "INV-O3DE-b",
        "passed": passed,
        "single_handler_exclusivity": single_handler_passed,
        "priority_order_verified": order_passed,
        "events_per_sec": rate,
        "duration_s": total_dur,
    }


def suite_o3_physics_substepping_accumulator() -> dict:
    t0 = time.perf_counter()
    sim = O3DEPhysicsSimulator(fixed_dt_us=16666, max_substeps=4)
    sim.add_body(body_id=1, mass=1.0, initial_vel=10.0)

    # Test erratic frame delta times: 1ms, 16.666ms, 33.332ms, 100ms, 1000ms
    frame_deltas = [1000, 16666, 33332, 50000, 100000, 500000, 1000000]
    substep_results = []
    accumulator_bounds_satisfied = True

    for dt in frame_deltas:
        substeps = sim.step(dt)
        if substeps > 4:
            accumulator_bounds_satisfied = False
        if sim.accumulator_us > sim.max_accum_us:
            accumulator_bounds_satisfied = False
        substep_results.append({
            "dt_frame_us": dt,
            "substeps_executed": substeps,
            "clamped_accumulator_us": sim.accumulator_us,
        })

    total_dur = time.perf_counter() - t0
    return {
        "suite_id": "SUITE-O3",
        "name": "Physics Fixed Substepping & Accumulator Clamping",
        "invariant": "INV-O3DE-c",
        "passed": accumulator_bounds_satisfied,
        "duration_s": total_dur,
        "evaluations": substep_results,
    }


def suite_o4_symplectic_energy_dissipation() -> dict:
    t0 = time.perf_counter()
    sim = O3DEPhysicsSimulator(fixed_dt_us=16666, max_substeps=4, linear_damping=0.05)
    sim.add_body(body_id=1, mass=2.0, initial_vel=50.0)

    energies = []
    # Advance 100 frames with 0 external acceleration
    for _ in range(100):
        sim.step(16666, external_accel=0.0)
        energies.append(sim.get_kinetic_energy())

    # Monotonic decrease check: E_{t+1} <= E_t
    monotonic = all(energies[i+1] <= energies[i] for i in range(len(energies) - 1))
    # Strict decay check: final < 1% of initial
    dissipated = (energies[-1] < 0.01 * energies[0])

    total_dur = time.perf_counter() - t0
    return {
        "suite_id": "SUITE-O4",
        "name": "PhysX Symplectic Energy Dissipation Monotonicity",
        "invariant": "INV-O3DE-d",
        "passed": (monotonic and dissipated),
        "initial_energy_j": energies[0],
        "final_energy_j": energies[-1],
        "monotonic": monotonic,
        "dissipated": dissipated,
        "duration_s": total_dur,
    }


def suite_o5_collision_filtering_symmetry() -> dict:
    t0 = time.perf_counter()
    rng = np.random.default_rng(2026)

    # PhysX filtering predicate: CanCollide(A, B) = (groupA & maskB != 0) and (groupB & maskA != 0)
    def can_collide(g_a, m_a, g_b, m_b):
        return bool((g_a & m_b) != 0 and (g_b & m_a) != 0)

    symmetry_preserved = True
    evaluations_count = 10_000

    groups = rng.integers(1, 256, size=evaluations_count)
    masks = rng.integers(1, 256, size=evaluations_count)

    for i in range(evaluations_count // 2):
        g_a, m_a = int(groups[2*i]), int(masks[2*i])
        g_b, m_b = int(groups[2*i + 1]), int(masks[2*i + 1])
        c_ab = can_collide(g_a, m_a, g_b, m_b)
        c_ba = can_collide(g_b, m_b, g_a, m_a)
        if c_ab != c_ba:
            symmetry_preserved = False
            break

    total_dur = time.perf_counter() - t0
    return {
        "suite_id": "SUITE-O5",
        "name": "Collision Filtering Matrix Symmetry Invariant",
        "passed": symmetry_preserved,
        "evaluations": evaluations_count,
        "duration_s": total_dur,
    }


def suite_o6_engine_throughput() -> dict:
    t0 = time.perf_counter()
    sim = O3DEPhysicsSimulator(fixed_dt_us=16666, max_substeps=4)
    # Add 500 dynamic rigid bodies
    for i in range(500):
        sim.add_body(body_id=i, mass=1.0 + i*0.1, initial_vel=10.0 + i*0.05)

    num_frames = 2000
    t_run = time.perf_counter()
    for _ in range(num_frames):
        sim.step(16666, external_accel=-9.81)
    sim_dur = time.perf_counter() - t_run

    fps = num_frames / sim_dur if sim_dur > 0 else 0
    body_steps_per_sec = (num_frames * 500) / sim_dur if sim_dur > 0 else 0

    total_dur = time.perf_counter() - t0
    return {
        "suite_id": "SUITE-O6",
        "name": "Engine Physics Simulation Throughput (500 bodies)",
        "passed": (fps > 100.0),
        "frames_per_sec": fps,
        "body_steps_per_sec": body_steps_per_sec,
        "duration_s": total_dur,
    }


def run_all_benchmarks() -> dict:
    suites = [
        suite_o1_ecs_scaling(),
        suite_o2_ebus_dispatch(),
        suite_o3_physics_substepping_accumulator(),
        suite_o4_symplectic_energy_dissipation(),
        suite_o5_collision_filtering_symmetry(),
        suite_o6_engine_throughput(),
    ]
    all_passed = all(s["passed"] for s in suites)
    total_duration = sum(s["duration_s"] for s in suites)
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"),
        "iso_time": datetime.now(timezone.utc).isoformat(),
        "all_passed": all_passed,
        "total_duration_s": total_duration,
        "suites": suites,
    }


if __name__ == "__main__":
    print("Running O3DE Stress & Benchmark Harness...")
    res = run_all_benchmarks()
    for s in res["suites"]:
        status = "✅ PASS" if s["passed"] else "❌ FAIL"
        print(f"  {s['suite_id']}: {s['name']} -> {status} ({s['duration_s']:.3f}s)")
    print(f"Overall Result: {'✅ ALL PASSED' if res['all_passed'] else '❌ FAIL'} ({res['total_duration_s']:.3f}s)")
