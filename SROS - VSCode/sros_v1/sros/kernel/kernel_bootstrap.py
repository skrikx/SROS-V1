from .event_bus import EventBus
from .daemon_registry import DaemonRegistry
from .daemons.heartbeat_daemon import HeartbeatDaemon
from .daemons.scheduler_daemon import SchedulerDaemon
from .daemons.health_daemon import HealthDaemon
from .daemons.memory_daemon import MemoryDaemon
from .daemons.adapter_daemon import AdapterDaemon
from .daemons.agent_router_daemon import AgentRouterDaemon
from ..memory.memory_router import MemoryRouter
from ..mirroros.trace_store import TraceStore
from ..mirroros.witness import Witness
from ..router.task_router import TaskRouter

class KernelContext:
    def __init__(self, event_bus, memory, registry, witness=None, router=None, tool_router=None):
        self.event_bus = event_bus
        self.memory = memory
        self.registry = registry
        self.witness = witness
        self.router = router  # SRX Task Router
        self.tool_router = tool_router # Sovereign Tool Router

def boot(config_path: str = "sros_config.yml") -> KernelContext:
    print(f"Booting SROS Kernel (config={config_path})...")
    
    # 1. Initialize Event Bus
    event_bus = EventBus()
    
    # 2. Initialize Memory
    memory = MemoryRouter()
    
    # Initialize Memory Layers
    from ..memory.short_term_memory import ShortTermMemory
    from ..memory.long_term_memory import LongTermMemory
    from ..memory.codex_memory import CodexMemory
    from ..memory.vector_store import VectorStore
    
    short_term = ShortTermMemory()
    long_term = LongTermMemory()
    codex = CodexMemory()
    vector_store = VectorStore()
    
    memory.initialize_layers(
        short_term=short_term,
        long_term=long_term,
        codex=codex,
        vector_store=vector_store
    )
    
    # 3. Initialize MirrorOS (Witness & Trace Store)
    trace_store = TraceStore(storage_path="./data/traces/sros_trace.jsonl")
    witness = Witness(trace_store)
    
    # 4. Initialize Registry
    registry = DaemonRegistry(event_bus)
    
    # 5. Initialize SRX Task Router (multi-model routing)
    # Router integrates adapter registry and event bus for routing decisions
    router = TaskRouter(adapter_registry={}, event_bus=event_bus)

    # 5b. Initialize Tool Router (Sovereign Tooling)
    from ..runtime.tool_router import ToolRouter
    tool_router = ToolRouter(event_bus)
    
    # 6. Register Core Daemons (Tier 1: Essential)
    registry.register("heartbeat", HeartbeatDaemon(event_bus))
    registry.register("scheduler", SchedulerDaemon(event_bus))
    registry.register("health", HealthDaemon(event_bus))
    
    # 7. Register Support Daemons (Tier 2: Infrastructure)
    registry.register("memory", MemoryDaemon(event_bus, memory_router=memory))
    registry.register("adapter", AdapterDaemon(event_bus))
    registry.register("agent_router", AgentRouterDaemon(event_bus))
    
    # 8. Register Sovereign Daemons (Tier 3: Autonomy)
    from ..daemons.ouroboros_daemon import OuroborosDaemon
    from ..daemons.self_healing_daemon import SelfHealingDaemon
    # Pass partial context or just components. 
    # OuroborosDaemon expects kernel_context.
    partial_context = KernelContext(event_bus, memory, registry, witness, router, tool_router)
    registry.register("ouroboros", OuroborosDaemon(partial_context))
    registry.register("self_healing", SelfHealingDaemon(partial_context))
    
    # 9. Start All Daemons
    registry.start_all()
    
    event_bus.publish("kernel", "kernel.ready", {})
    print("SROS Kernel Online (8 daemons active, SRX router enabled, Singularity Mode).")
    
    return KernelContext(event_bus, memory, registry, witness, router, tool_router)
