#!/usr/bin/env python3
"""
O3DE Core Engine & Simulation Runtime Harness
Subsystem: /run/media/multiplic/AGI/prismagi/mount/SUBSYSTEMS/o3de-prism
Origin: /run/media/multiplic/AGI/prismagi/mount/SUBSYSTEMS/o3de
Formalization: LexLean Language 1.2 / Lean 4 Kernel Attested
Governed by: ADR-0025, ADR-0026, and Multiplicity Theory Formal Framework
"""

import math
import heapq
import time
from typing import Dict, List, Set, Tuple, Optional
import numpy as np


class O3DEECSSimulator:
    """Simulates AZCore Component Entity System activation & dependency resolution."""
    def __init__(self, max_components_per_entity: int = 64):
        self.max_components = max_components_per_entity
        self.entities: Dict[int, Dict[str, any]] = {}

    def create_entity(self, entity_id: int) -> dict:
        self.entities[entity_id] = {
            "id": entity_id,
            "state": "uninitialized",
            "components": [],
            "active_services": set(),
        }
        return self.entities[entity_id]

    def add_component(
        self,
        entity_id: int,
        component_id: int,
        provided: int,
        required: int = 0,
        incompatible: int = 0,
    ) -> bool:
        if entity_id not in self.entities:
            self.create_entity(entity_id)
        ent = self.entities[entity_id]
        if len(ent["components"]) >= self.max_components:
            return False
        ent["components"].append({
            "component_id": component_id,
            "provided": provided,
            "required": required,
            "incompatible": incompatible,
            "active": False,
        })
        return True

    def activate_entity(self, entity_id: int) -> Tuple[bool, List[int]]:
        """
        Activates components in topological order satisfying service requirements
        and verifying mutual exclusivity. Returns (success, activation_order).
        """
        if entity_id not in self.entities:
            return False, []
        ent = self.entities[entity_id]
        active_services: Set[int] = set()
        components = list(ent["components"])
        activation_order: List[int] = []

        # Iteratively activate components whose requirements are satisfied
        changed = True
        while changed and components:
            changed = False
            remaining = []
            for comp in components:
                req = comp["required"]
                incomp = comp["incompatible"]
                # Requirement check
                req_ok = (req == 0 or req in active_services)
                # Incompatibility check
                incomp_ok = (incomp == 0 or incomp not in active_services)

                if req_ok and incomp_ok:
                    active_services.add(comp["provided"])
                    comp["active"] = True
                    activation_order.append(comp["component_id"])
                    changed = True
                else:
                    remaining.append(comp)
            components = remaining

        success = (len(components) == 0)
        ent["state"] = "active" if success else "suspended"
        ent["active_services"] = active_services
        return success, activation_order


class O3DEEBusSimulator:
    """Simulates AZCore::EBus priority-ordered event dispatch and handler policy."""
    def __init__(self, bus_id: int, is_single_handler: bool = False):
        self.bus_id = bus_id
        self.is_single_handler = is_single_handler
        self.handlers: List[Tuple[int, int]] = []  # (-priority, handler_id)

    def connect(self, handler_id: int, priority: int = 0) -> bool:
        if self.is_single_handler and len(self.handlers) > 0:
            return False
        heapq.heappush(self.handlers, (-priority, handler_id))
        return True

    def dispatch(self, event_data: any) -> List[int]:
        """Dispatches event to handlers in strict descending priority order."""
        # Drain in priority order
        sorted_handlers = sorted(self.handlers, key=lambda x: x[0])
        return [h_id for _, h_id in sorted_handlers]


class O3DEPhysicsSimulator:
    """Simulates PhysX fixed-substepping rigid body solver with symplectic integration."""
    def __init__(
        self,
        fixed_dt_us: int = 16666,
        max_substeps: int = 4,
        linear_damping: float = 0.05,
        max_velocity: float = 100.0,
    ):
        self.fixed_dt_s = fixed_dt_us / 1_000_000.0
        self.fixed_dt_us = fixed_dt_us
        self.max_substeps = max_substeps
        self.max_accum_us = fixed_dt_us * max_substeps
        self.linear_damping = linear_damping
        self.max_velocity = max_velocity
        self.accumulator_us = 0

        # Rigid bodies: id -> {mass, pos, vel, is_kinematic}
        self.bodies: Dict[int, Dict[str, any]] = {}

    def add_body(
        self,
        body_id: int,
        mass: float,
        is_kinematic: bool = False,
        initial_vel: float = 0.0,
        initial_pos: float = 0.0,
    ):
        self.bodies[body_id] = {
            "mass": mass,
            "is_kinematic": is_kinematic,
            "vel": initial_vel,
            "pos": initial_pos,
        }

    def step(self, dt_frame_us: int, external_accel: float = 0.0) -> int:
        """
        Advances physics simulation by dt_frame_us with accumulator clamping
        preventing the spiral-of-death numerical collapse.
        Returns the number of sub-steps executed.
        """
        self.accumulator_us += dt_frame_us
        if self.accumulator_us > self.max_accum_us:
            self.accumulator_us = self.max_accum_us

        substeps = 0
        while self.accumulator_us >= self.fixed_dt_us and substeps < self.max_substeps:
            self._integrate_substep(external_accel)
            self.accumulator_us -= self.fixed_dt_us
            substeps += 1

        return substeps

    def _integrate_substep(self, accel: float):
        for b in self.bodies.values():
            if b["is_kinematic"]:
                b["vel"] = 0.0
                continue

            # Symplectic Euler: integrate velocity with external acceleration & damping
            raw_vel = b["vel"] + accel * self.fixed_dt_s
            damped_vel = raw_vel * (1.0 - self.linear_damping)
            
            # Velocity clamping
            if abs(damped_vel) > self.max_velocity:
                damped_vel = math.copysign(self.max_velocity, damped_vel)

            b["vel"] = damped_vel
            b["pos"] += damped_vel * self.fixed_dt_s

    def get_kinetic_energy(self) -> float:
        total_ke = 0.0
        for b in self.bodies.values():
            if not b["is_kinematic"]:
                total_ke += 0.5 * b["mass"] * (b["vel"] ** 2)
        return total_ke
