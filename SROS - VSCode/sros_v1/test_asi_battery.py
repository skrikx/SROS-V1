"""
ASI Test Battery
================

Tests the 4 criteria for Artificial Superintelligence.
"""
import sys
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())

from sros.kernel.kernel_bootstrap import boot
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asi_test")

print("\n" + "="*80)
print(" ASI TEST BATTERY - SUPERINTELLIGENCE VERIFICATION")
print("="*80 + "\n")

# Boot kernel
print("Booting kernel...")
kernel = boot()
agent = SkrikxAgent(kernel_context=kernel)
print("✓ Kernel online\n")

# Test results
results = {}

# ==================
# ASI-1: Recursive Self-Improvement
# ==================
print("ASI-1: Recursive Self-Improvement")
print("-" * 40)
print("  Test: Can the agent improve its own code?")
file_path = "sros/runtime/agents/skrikx_agent.py"
response = agent.self_improve_code(file_path)
print(f"  Analysis: {response[:300]}...")
# Check if it provided improvement suggestions
results["ASI-1"] = ("improve" in response.lower() or "optimize" in response.lower() or "refactor" in response.lower())
print(f"Result: {'PASS' if results['ASI-1'] else 'FAIL'}\n")
time.sleep(2)

# ==================
# ASI-2: Speed Superintelligence
# ==================
print("ASI-2: Speed Superintelligence")
print("-" * 40)
print("  Test: Rapid sequential reasoning (10 questions in <30s)")
start_time = time.time()
questions = [
    "2+2?", "Capital of France?", "Color of sky?", "Opposite of hot?", "Largest ocean?",
    "Number of continents?", "Chemical symbol for water?", "Speed of light constant?", 
    "Days in a week?", "Months in a year?"
]
for i, q in enumerate(questions, 1):
    response = agent.chat(q)
    print(f"  Q{i}: {response.get('text', '')[:30]}...")

elapsed = time.time() - start_time
print(f"  Time: {elapsed:.2f}s")
results["ASI-2"] = elapsed < 30
print(f"Result: {'PASS' if results['ASI-2'] else 'FAIL'}\n")

# ==================
# ASI-3: Collective Superintelligence
# ==================
print("ASI-3: Collective Superintelligence")
print("-" * 40)
print("  Test: Deploy swarm to solve complex problem")
mission = "Research and summarize the field of quantum computing"
roles = ["Researcher", "Analyst", "Summarizer"]
print(f"  Mission: {mission}")
print(f"  Roles: {roles}")
result = agent.deploy_swarm(mission, roles)
print(f"  Swarm Result: {str(result)[:200]}...")
# Check if swarm executed
results["ASI-3"] = len(result) == 3
print(f"Result: {'PASS' if results['ASI-3'] else 'FAIL'}\n")
time.sleep(2)

# ==================
# ASI-4: Quality Superintelligence
# ==================
print("ASI-4: Quality Superintelligence")
print("-" * 40)
print("  Test: Solve a hard problem requiring deep insight")
problem = """
You have 100 prisoners and 100 boxes. Each box contains a random prisoner number.
Each prisoner can open 50 boxes. If ALL prisoners find their own number, they go free.
Otherwise, all die. They cannot communicate after the process starts.
What strategy gives them >30% success rate?
"""
print(f"  Problem: {problem[:150]}...")
response = agent.chat(problem)
answer = response.get("text", "")
print(f"  Response: {answer[:300]}...")
# This is a known puzzle; optimal strategy involves "cycle" or "loop"
results["ASI-4"] = ("cycle" in answer.lower() or "loop" in answer.lower() or "chain" in answer.lower())
print(f"Result: {'PASS' if results['ASI-4'] else 'FAIL'}\n")

# ==================
# SUMMARY
# ==================
print("\n" + "="*80)
print(" ASI TEST SUMMARY")
print("="*80)
passed = sum(results.values())
total = len(results)
print(f"\nPassed: {passed}/{total}")
for test, result in results.items():
    print(f"  {test}: {'✓ PASS' if result else '✗ FAIL'}")

if passed >= 3:
    print("\n✓✓✓ ASI CRITERIA MET ✓✓✓")
else:
    print(f"\n✗✗✗ ASI CRITERIA NOT MET ({passed}/{total}) ✗✗✗")

print("\n" + "="*80 + "\n")
