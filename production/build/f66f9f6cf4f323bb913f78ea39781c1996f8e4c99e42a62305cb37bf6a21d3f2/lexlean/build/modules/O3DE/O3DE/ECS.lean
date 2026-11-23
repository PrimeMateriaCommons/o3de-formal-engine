module
public import Init
public import O3DE.O3DE.Parameters
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 1000000000
set_option linter.constructorNameAsVariable false
namespace O3DE.O3DE.ECS

public inductive EntityState where
  | uninitialized
  | initialized
  | active
  | suspended

public structure ComponentDescriptor where
  componentId : Nat
  entityId : Nat
  providedServiceId : Nat
  requiredServiceId : Nat
  incompatibleServiceId : Nat

public structure EntityRecord where
  entityId : Nat
  state : EntityState
  componentCount : Nat
  activeServiceId : Nat

@[expose] public def isActivationAdmissible (reqId : Nat) (incompId : Nat) (currentActiveService : Nat) : Bool := (((Nat.beq (reqId) (0)) || (Nat.beq (reqId) (currentActiveService))) && ((Nat.beq (incompId) (0)) || (!(Nat.beq (incompId) (currentActiveService)))))

@[expose] public def defaultTransformComponent : ComponentDescriptor := ({ componentId := 101, entityId := 1, providedServiceId := 1, requiredServiceId := 0, incompatibleServiceId := 0 } : ComponentDescriptor)

@[expose] public def defaultRigidBodyComponent : ComponentDescriptor := ({ componentId := 102, entityId := 1, providedServiceId := 2, requiredServiceId := 1, incompatibleServiceId := 3 } : ComponentDescriptor)

public theorem transform_activates_unconditionally : (isActivationAdmissible ((defaultTransformComponent).requiredServiceId) ((defaultTransformComponent).incompatibleServiceId) (0) = true) := by
  rfl

public theorem rigidbody_activates_with_transform : (isActivationAdmissible ((defaultRigidBodyComponent).requiredServiceId) ((defaultRigidBodyComponent).incompatibleServiceId) (1) = true) := by
  rfl

public theorem rigidbody_blocked_without_transform : (isActivationAdmissible ((defaultRigidBodyComponent).requiredServiceId) ((defaultRigidBodyComponent).incompatibleServiceId) (0) = false) := by
  rfl

public theorem rigidbody_blocked_by_incompatible : (isActivationAdmissible ((defaultRigidBodyComponent).requiredServiceId) ((defaultRigidBodyComponent).incompatibleServiceId) (3) = false) := by
  rfl

public theorem entity_activation_deterministic : ((let t : Bool := isActivationAdmissible (1) (3) (1); (let f : Bool := isActivationAdmissible (1) (3) (0); (t && (!f)))) = true) := by
  rfl

end O3DE.O3DE.ECS
