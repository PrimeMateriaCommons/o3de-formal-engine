module
public import Init
public import O3DE.O3DE.EBus
public import O3DE.O3DE.ECS
public import O3DE.O3DE.Invariants
public import O3DE.O3DE.Parameters
public import O3DE.O3DE.Physics
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 1000000000
set_option linter.constructorNameAsVariable false
namespace O3DE.Main

public theorem o3de_physics_substepping_sound : ((O3DE.O3DE.Parameters.isSubsteppingStable (O3DE.O3DE.Parameters.defaultPhysicsParams) && ((Nat.beq (O3DE.O3DE.Invariants.computeSubsteps (33332) (16666) (4)) (2)) && (Nat.beq (O3DE.O3DE.Invariants.clampAccumulator (100000) (66664)) (66664)))) = true) := by
  rfl

public theorem o3de_ecs_activation_sound : ((O3DE.O3DE.ECS.isActivationAdmissible (1) (3) (1) && (!O3DE.O3DE.ECS.isActivationAdmissible (1) (3) (3))) = true) := by
  rfl

public theorem o3de_ebus_single_handler_invariant : ((O3DE.O3DE.EBus.canConnectHandler (true) (0) && (!O3DE.O3DE.EBus.canConnectHandler (true) (1))) = true) := by
  rfl

public theorem o3de_physx_energy_dissipation_invariant : ((Nat.beq (O3DE.O3DE.Physics.integrateVelocityStep (O3DE.O3DE.Physics.dynamicBody) (0) (16) (50)) (9500)) = true) := by
  rfl

public theorem o3de_end_to_end_frame_budget_sound : (((Nat.beq (O3DE.O3DE.Parameters.maxAccumulatedTimeUs (O3DE.O3DE.Parameters.defaultPhysicsParams)) (66664)) && O3DE.O3DE.Invariants.isCollisionFiltered (1) (2) (2) (1)) = true) := by
  rfl

end O3DE.Main
