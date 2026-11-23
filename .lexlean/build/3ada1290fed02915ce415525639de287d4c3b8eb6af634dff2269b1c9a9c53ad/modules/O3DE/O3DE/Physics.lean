module
public import Init
public import LexLeanRuntime.Portable
public import O3DE.O3DE.Invariants
public import O3DE.O3DE.Parameters
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 1000000000
set_option linter.constructorNameAsVariable false
namespace O3DE.O3DE.Physics

public structure PhysXRigidBody where
  bodyId : Nat
  massGrams : Nat
  isKinematic : Bool
  velocityScaled : Nat
  maxVelocityScaled : Nat

@[expose] public def kinematicBody : PhysXRigidBody := ({ bodyId := 1, massGrams := 0, isKinematic := true, velocityScaled := 0, maxVelocityScaled := 50000 } : PhysXRigidBody)

@[expose] public def dynamicBody : PhysXRigidBody := ({ bodyId := 2, massGrams := 2000, isKinematic := false, velocityScaled := 10000, maxVelocityScaled := 50000 } : PhysXRigidBody)

@[expose] public def integrateVelocityStep (body : PhysXRigidBody) (accelScaled : Nat) (dtMs : Nat) (dampingScaled : Nat) : Nat := (if (body).isKinematic then 0 else (let rawVel : Nat := ((body).velocityScaled + (LexLeanRuntime.quotient ((LexLeanRuntime.multiply (accelScaled) (dtMs) : Nat)) (1000) (0) : Nat)); (let dampedVel : Nat := O3DE.O3DE.Invariants.applyVelocityDamping (rawVel) (dampingScaled); (if (Nat.ble (dampedVel) ((body).maxVelocityScaled)) then dampedVel else (body).maxVelocityScaled))))

@[expose] public def computeKineticEnergyScaled (massGrams : Nat) (velocityScaled : Nat) : Nat := (LexLeanRuntime.quotient ((LexLeanRuntime.multiply (massGrams) ((LexLeanRuntime.multiply (velocityScaled) (velocityScaled) : Nat)) : Nat)) (2000) (0) : Nat)

public theorem kinematic_velocity_invariant_zero : (integrateVelocityStep (kinematicBody) (5000) (16) (50) = 0) := by
  rfl

public theorem dynamic_velocity_step_calculation : (integrateVelocityStep (dynamicBody) (0) (16) (50) = 9500) := by
  rfl

public theorem velocity_clamped_at_maximum : (integrateVelocityStep (dynamicBody) (5000000) (100) (0) = 50000) := by
  rfl

public theorem kinetic_energy_soundness : (computeKineticEnergyScaled (2000) (100) = 10000) := by
  rfl

end O3DE.O3DE.Physics
