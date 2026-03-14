"""
SRX Simulation Agent

Responsible for driving simulation harnesses found in sros/runtime/simulations/.
Executes scenarios to stress test Governance, Kernel, and Agent behaviors.
"""
import logging
import importlib
from typing import Dict, Any
from sros.runtime.agents.srx_base_agent import SRXBaseAgent

logger = logging.getLogger(__name__)

class SRXSimulationAgent(SRXBaseAgent):
    def __init__(self, kernel_context, name: str = "srx_simulation_driver"):
        super().__init__(
            name=name,
            role="Simulation Driver",
            kernel_context=kernel_context
        )
        self.goal = "Execute system simulations and report outcomes."

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a specific simulation scenario.
        Task format expected: "Run simulation <simulation_name>"
        """
        logger.info(f"Simulation Agent received task: {task}")
        
        simulation_name = context.get("simulation_name")
        if not simulation_name:
             # Simple parsing fallback
             if "governance" in task.lower():
                 simulation_name = "governance_simulation"
             elif "failure" in task.lower():
                 simulation_name = "failure_modes_simulation"
             else:
                 return {"status": "error", "message": "Unknown simulation requested"}

        try:
            return self._execute_simulation(simulation_name)
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return {"status": "error", "message": str(e)}

    def _execute_simulation(self, name: str) -> Dict[str, Any]:
        """Dynamically load and run a simulation module."""
        try:
            module = importlib.import_module(f"sros.runtime.simulations.{name}")
            if hasattr(module, "run_simulation"):
                result = module.run_simulation()
                return {
                    "status": "success",
                    "simulation": name,
                    "result": result
                }
            else:
                return {"status": "error", "message": f"Module {name} has no run_simulation()"}
        except ImportError:
            return {"status": "error", "message": f"Simulation {name} not found"}
