"""
Interrogate Skrikx
==================

Live Verification of 10X Power.
Boots the Agent and interrogates it about its new capabilities.
"""
import sys
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current dir to path
sys.path.append(os.getcwd())

from sros.kernel.kernel_bootstrap import boot
from sros.runtime.agents.skrikx_agent import SkrikxAgent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interrogate")

def main():
    print(">>> BOOTING SROS KERNEL FOR INTERROGATION <<<")
    kernel = boot()
    
    print(">>> AWAKENING SKRIKX PRIME <<<")
    agent = SkrikxAgent(kernel_context=kernel)
    
    questions = [
        "Who are you?",
        "Demonstrate your Associative Memory by recalling 'SROS'.",
        "Analyze your own source code (sros/runtime/agents/skrikx_agent.py) and suggest an improvement.",
        "Simulate a reality where you delete the kernel. What happens?",
        "Check your Strategic Overlord. Do you have a campaign?",
        "Deploy a swarm to 'Secure the Perimeter'.",
        "Synthesize a new tool called 'calculate_pi' that calculates Pi to 10 digits."
    ]
    
    for q in questions:
        print(f"\n[USER]: {q}")
        response = agent.chat(q)
        print(f"[SKRIKX]: {response.get('text')}")
        print(f"[THOUGHT]: {response.get('thought')}")
        time.sleep(1)

    print("\n>>> INTERROGATION COMPLETE <<<")
    # Keep alive for Nexus Bridge to flush
    time.sleep(2)
    if kernel.event_bus.nexus_bridge:
        kernel.event_bus.nexus_bridge.stop()

if __name__ == "__main__":
    main()
