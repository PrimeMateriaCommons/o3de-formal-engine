module
public import Init
public import LexLeanRuntime.Portable
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 1000000000
set_option linter.constructorNameAsVariable false
namespace O3DE.O3DE.Parameters

public structure O3DEPhysicsParameters where
  fixedTimestepUs : Nat
  maxSubsteps : Nat
  positionSolverIterations : Nat
  velocitySolverIterations : Nat
  linearDampingScaled : Nat
  angularDampingScaled : Nat
  maxVelocityScaled : Nat

public structure O3DEECSParameters where
  maxComponentsPerEntity : Nat
  maxEntitiesCapacity : Nat
  systemServiceSlots : Nat

public structure O3DEEBusParameters where
  defaultQueueCapacity : Nat
  maxHandlersPerBus : Nat

@[expose] public def defaultPhysicsParams : O3DEPhysicsParameters := ({ fixedTimestepUs := 16666, maxSubsteps := 4, positionSolverIterations := 8, velocitySolverIterations := 2, linearDampingScaled := 50, angularDampingScaled := 50, maxVelocityScaled := 100000 } : O3DEPhysicsParameters)

@[expose] public def highPrecisionPhysicsParams : O3DEPhysicsParameters := ({ fixedTimestepUs := 8333, maxSubsteps := 8, positionSolverIterations := 16, velocitySolverIterations := 4, linearDampingScaled := 50, angularDampingScaled := 50, maxVelocityScaled := 100000 } : O3DEPhysicsParameters)

@[expose] public def defaultECSParams : O3DEECSParameters := ({ maxComponentsPerEntity := 64, maxEntitiesCapacity := 100000, systemServiceSlots := 32 } : O3DEECSParameters)

@[expose] public def defaultEBusParams : O3DEEBusParameters := ({ defaultQueueCapacity := 4096, maxHandlersPerBus := 1024 } : O3DEEBusParameters)

@[expose] public def maxAccumulatedTimeUs (p : O3DEPhysicsParameters) : Nat := (LexLeanRuntime.multiply ((p).maxSubsteps) ((p).fixedTimestepUs) : Nat)

@[expose] public def isSubsteppingStable (p : O3DEPhysicsParameters) : Bool := (((Nat.ble (4) ((p).positionSolverIterations)) && (Nat.ble (1) ((p).velocitySolverIterations))) && (Nat.ble (1) ((p).maxSubsteps)))

public theorem default_physics_stable : (isSubsteppingStable (defaultPhysicsParams) = true) := by
  rfl

public theorem high_precision_physics_stable : (isSubsteppingStable (highPrecisionPhysicsParams) = true) := by
  rfl

public theorem default_max_accum_time : (maxAccumulatedTimeUs (defaultPhysicsParams) = 66664) := by
  rfl

public theorem high_precision_max_accum_time : (maxAccumulatedTimeUs (highPrecisionPhysicsParams) = 66664) := by
  rfl

public theorem ecs_capacity_nominal : ((defaultECSParams).maxEntitiesCapacity = 100000) := by
  rfl

public theorem ebus_capacity_nominal : ((defaultEBusParams).defaultQueueCapacity = 4096) := by
  rfl

end O3DE.O3DE.Parameters
