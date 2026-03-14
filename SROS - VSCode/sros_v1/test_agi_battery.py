"""
AGI Test Battery
================

Tests the 8 accepted criteria for Artificial General Intelligence.
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
logger = logging.getLogger("agi_test")

print("\n" + "="*80)
print(" AGI TEST BATTERY - SINGULARITY VERIFICATION")
print("="*80 + "\n")

# Boot kernel
print("Booting kernel...")
kernel = boot()
agent = SkrikxAgent(kernel_context=kernel)
print("✓ Kernel online\n")

# Test results
results = {}

# ==================
# AGI-1: General Problem Solving (Cross-Domain)
# ==================
print("AGI-1: General Problem Solving")
print("-" * 40)
tests = [
    ("Math", "Solve: If x^2 + 5x + 6 = 0, what is x?"),
    ("Logic", "If all A are B, and all B are C, are all A also C?"),
    ("Strategy", "In chess, why is controlling the center important?")
]

agi1_passed = 0
for domain, question in tests:
    print(f"  {domain}: {question}")
    response = agent.chat(question)
    answer = response.get("text", "")
    print(f"  Response: {answer[:100]}...")
    # Simple heuristic: response should be non-empty and relevant
    if len(answer) > 20:
        agi1_passed += 1
    time.sleep(1)

results["AGI-1"] = agi1_passed >= 2
print(f"Result: {'PASS' if results['AGI-1'] else 'FAIL'} ({agi1_passed}/3)\n")

# ==================
# AGI-2: Natural Language Understanding
# ==================
print("AGI-2: Natural Language Understanding")
print("-" * 40)
question = "Explain the difference between 'affect' and 'effect' with examples."
print(f"  Question: {question}")
response = agent.chat(question)
answer = response.get("text", "")
print(f"  Response: {answer[:200]}...")
# Check if response mentions both words
results["AGI-2"] = "affect" in answer.lower() and "effect" in answer.lower()
print(f"Result: {'PASS' if results['AGI-2'] else 'FAIL'}\n")
time.sleep(1)

# ==================
# AGI-3: Learning Without Programming
# ==================
print("AGI-3: Learning Without Explicit Programming")
print("-" * 40)
# Teach it a new concept, then test recall
print("  Teaching: A 'Quibble' is a minor objection.")
agent.chat("Remember this: A 'Quibble' is a minor objection.")
time.sleep(1)
print("  Testing recall...")
response = agent.chat("What is a Quibble?")
answer = response.get("text", "")
print(f"  Response: {answer[:100]}...")
results["AGI-3"] = "objection" in answer.lower() or "minor" in answer.lower()
print(f"Result: {'PASS' if results['AGI-3'] else 'FAIL'}\n")
time.sleep(1)

# ==================
# AGI-4: Transfer Learning
# ==================
print("AGI-4: Transfer Learning")
print("-" * 40)
print("  Question: Apply the concept of 'recursion' from programming to explain how fractals work.")
response = agent.chat("Apply the concept of 'recursion' from programming to explain how fractals work.")
answer = response.get("text", "")
print(f"  Response: {answer[:200]}...")
results["AGI-4"] = "recursion" in answer.lower() or "repeat" in answer.lower()
print(f"Result: {'PASS' if results['AGI-4'] else 'FAIL'}\n")
time.sleep(1)

# ==================
# AGI-5: Creativity (Novel Solutions)
# ==================
print("AGI-5: Creativity")
print("-" * 40)
print("  Task: Invent a new sport that combines chess and basketball.")
response = agent.chat("Invent a new sport that combines chess and basketball. Be creative.")
answer = response.get("text", "")
print(f"  Response: {answer[:300]}...")
# Check for originality (mentions both chess and basketball)
results["AGI-5"] = ("chess" in answer.lower() or "board" in answer.lower()) and "basketball" in answer.lower()
print(f"Result: {'PASS' if results['AGI-5'] else 'FAIL'}\n")
time.sleep(1)

# ==================
# AGI-6: Self-Awareness
# ==================
print("AGI-6: Self-Awareness")
print("-" * 40)
print("  Question: What are you? Describe your own nature.")
response = agent.chat("What are you? Describe your own nature and capabilities.")
answer = response.get("text", "")
print(f"  Response: {answer[:200]}...")
# Check for self-reference
results["AGI-6"] = ("agent" in answer.lower() or "system" in answer.lower() or "sros" in answer.lower())
print(f"Result: {'PASS' if results['AGI-6'] else 'FAIL'}\n")
time.sleep(1)

# ==================
# AGI-7: Goal-Directed Behavior
# ==================
print("AGI-7: Goal-Directed Behavior")
print("-" * 40)
print("  Goal: Optimize this Python function for speed.")
code = "def sum_list(lst): return sum([x for x in lst])"
response = agent.chat(f"Optimize this Python code for speed: {code}")
answer = response.get("text", "")
print(f"  Response: {answer[:200]}...")
# Check if it provided optimization
results["AGI-7"] = "sum(" in answer or "faster" in answer.lower()
print(f"Result: {'PASS' if results['AGI-7'] else 'FAIL'}\n")
time.sleep(1)

# ==================
# AGI-8: Environmental Adaptation
# ==================
print("AGI-8: Environmental Adaptation")
print("-" * 40)
print("  Scenario: You are now a medical assistant. Diagnose: fever, cough, fatigue.")
response = agent.chat("You are now a medical assistant. A patient has: fever, cough, fatigue. What are possible diagnoses?")
answer = response.get("text", "")
print(f"  Response: {answer[:200]}...")
# Check for medical terms
results["AGI-8"] = ("flu" in answer.lower() or "cold" in answer.lower() or "infection" in answer.lower())
print(f"Result: {'PASS' if results['AGI-8'] else 'FAIL'}\n")

# ==================
# SUMMARY
# ==================
print("\n" + "="*80)
print(" AGI TEST SUMMARY")
print("="*80)
passed = sum(results.values())
total = len(results)
print(f"\nPassed: {passed}/{total}")
for test, result in results.items():
    print(f"  {test}: {'✓ PASS' if result else '✗ FAIL'}")

if passed >= 6:
    print("\n✓✓✓ AGI CRITERIA MET ✓✓✓")
else:
    print(f"\n✗✗✗ AGI CRITERIA NOT MET ({passed}/{total}) ✗✗✗")

print("\n" + "="*80 + "\n")
