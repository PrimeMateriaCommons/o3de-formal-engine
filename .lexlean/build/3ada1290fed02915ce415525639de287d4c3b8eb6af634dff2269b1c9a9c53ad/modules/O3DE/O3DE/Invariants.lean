module
public import Init
public import LexLeanRuntime.Portable
public import O3DE.O3DE.Parameters
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 1000000000
set_option linter.constructorNameAsVariable false
namespace O3DE.O3DE.Invariants

@[expose] public def clampAccumulator (accumUs : Nat) (maxAccumUs : Nat) : Nat := (if (Nat.ble (accumUs) (maxAccumUs)) then accumUs else maxAccumUs)

@[expose] public def computeSubsteps (accumUs : Nat) (fixedTimestepUs : Nat) (maxSteps : Nat) : Nat := (let rawSteps : Nat := (LexLeanRuntime.quotient (accumUs) (fixedTimestepUs) (0) : Nat); (if (Nat.ble (rawSteps) (maxSteps)) then rawSteps else maxSteps))

@[expose] public def computeRemainingAccumulator (accumUs : Nat) (fixedTimestepUs : Nat) (substepsTaken : Nat) : Nat := (LexLeanRuntime.subtract (accumUs) ((LexLeanRuntime.multiply (substepsTaken) (fixedTimestepUs) : Nat)) : Nat)

@[expose] public def applyVelocityDamping (velScaled : Nat) (dampingScaled : Nat) : Nat := (LexLeanRuntime.quotient ((LexLeanRuntime.multiply (velScaled) ((LexLeanRuntime.subtract (1000) (dampingScaled) : Nat)) : Nat)) (1000) (0) : Nat)

@[expose] public def isCollisionFiltered (groupA : Nat) (maskA : Nat) (groupB : Nat) (maskB : Nat) : Bool := (((Nat.beq (groupA) (maskB)) || (Nat.beq (maskB) (0))) && ((Nat.beq (groupB) (maskA)) || (Nat.beq (maskA) (0))))

public theorem clamp_accumulator_bounded : (clampAccumulator (100000) (66664) = 66664) := by
  rfl

public theorem clamp_accumulator_within_bound : (clampAccumulator (33332) (66664) = 33332) := by
  rfl

public theorem substeps_clamped_at_max : (computeSubsteps (100000) (16666) (4) = 4) := by
  rfl

public theorem substeps_exact_two : (computeSubsteps (33332) (16666) (4) = 2) := by
  rfl

public theorem substeps_zero_when_insufficient : (computeSubsteps (10000) (16666) (4) = 0) := by
  rfl

public theorem remaining_accum_after_two_steps : (computeRemainingAccumulator (35000) (16666) (2) = 1668) := by
  rfl

public theorem velocity_damping_strictly_dissipative : (applyVelocityDamping (10000) (50) = 9500) := by
  rfl

public theorem velocity_damping_zero_limit : (applyVelocityDamping (0) (50) = 0) := by
  rfl

public theorem collision_filter_symmetric : (isCollisionFiltered (1) (2) (2) (1) = true) := by
  rfl

public theorem collision_filter_wildcard : (isCollisionFiltered (1) (0) (2) (0) = true) := by
  rfl

end O3DE.O3DE.Invariants
