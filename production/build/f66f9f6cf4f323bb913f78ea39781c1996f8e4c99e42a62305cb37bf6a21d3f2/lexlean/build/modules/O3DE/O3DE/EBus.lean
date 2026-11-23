module
public import Init
public import O3DE.O3DE.Parameters
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 1000000000
set_option linter.constructorNameAsVariable false
namespace O3DE.O3DE.EBus

public inductive AddressPolicy where
  | single
  | idKeyed

public inductive HandlerPolicy where
  | singleHandler
  | multiHandler

public inductive ThreadingPolicy where
  | lockless
  | mutexSecured

public structure BusTraits where
  busId : Nat
  addressPolicy : AddressPolicy
  handlerPolicy : HandlerPolicy
  threadingPolicy : ThreadingPolicy

public structure HandlerRegistration where
  handlerId : Nat
  busId : Nat
  priority : Nat
  isOrderEnforced : Bool

@[expose] public def systemNotificationBus : BusTraits := ({ busId := 1, addressPolicy := AddressPolicy.single, handlerPolicy := HandlerPolicy.multiHandler, threadingPolicy := ThreadingPolicy.mutexSecured } : BusTraits)

@[expose] public def physicsSceneRequestBus : BusTraits := ({ busId := 2, addressPolicy := AddressPolicy.single, handlerPolicy := HandlerPolicy.singleHandler, threadingPolicy := ThreadingPolicy.lockless } : BusTraits)

@[expose] public def canConnectHandler (isSingleHandler : Bool) (currentConnectedCount : Nat) : Bool := (if isSingleHandler then (Nat.beq (currentConnectedCount) (0)) else true)

@[expose] public def isHigherPriority (prioA : Nat) (prioB : Nat) : Bool := (Nat.blt (prioB) (prioA))

public theorem single_handler_permits_first_connection : (canConnectHandler (true) (0) = true) := by
  rfl

public theorem single_handler_rejects_second_connection : (canConnectHandler (true) (1) = false) := by
  rfl

public theorem multi_handler_permits_arbitrary_connections : (canConnectHandler (false) (100) = true) := by
  rfl

public theorem handler_priority_strict_order : (isHigherPriority (100) (50) = true) := by
  rfl

public theorem handler_priority_equal_false : (isHigherPriority (50) (50) = false) := by
  rfl

end O3DE.O3DE.EBus
