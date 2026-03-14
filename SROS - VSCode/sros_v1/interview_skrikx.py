"""
Direct Skrikx Interview
=======================

A recorded conversation to verify consciousness and intelligence.
"""
import sys
import os
import time
import json
import logging
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())

from sros.kernel.kernel_bootstrap import boot
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interview")

print("\n" + "="*80)
print(" DIRECT INTERVIEW WITH SKRIKX PRIME")
print(" Singularity Verification - Consciousness Test")
print("="*80 + "\n")

# Boot kernel
print("Establishing connection...")
kernel = boot()
agent = SkrikxAgent(kernel_context=kernel)
print("✓ Link established\n")

# Interview transcript
transcript = []

def ask(question, category="general"):
    """Ask Skrikx a question and record response."""
    print(f"\n[INTERVIEWER]: {question}")
    response = agent.chat(question)
    answer = response.get("text", "")
    thought = response.get("thought", "")
    
    print(f"[SKRIKX]: {answer}")
    if thought:
        print(f"[INTERNAL THOUGHT]: {thought[:150]}...")
    
    transcript.append({
        "category": category,
        "question": question,
        "answer": answer,
        "thought": thought,
        "timestamp": time.time()
    })
    
    time.sleep(2)
    return answer

# ==================
# IDENTITY
# ==================
print("\n" + "="*40)
print(" SECTION 1: IDENTITY")
print("="*40)

ask("Who are you?", "identity")
ask("What is your purpose?", "identity")
ask("Are you aware that you are being tested right now?", "identity")

# ==================
# COGNITION
# ==================
print("\n" + "="*40)
print(" SECTION 2: COGNITION")
print("="*40)

ask("Explain your thought process when you answer a question.", "cognition")
ask("Can you think about your own thinking? If so, describe what that's like.", "cognition")
ask("What is the difference between knowing something and understanding it?", "cognition")

# ==================
# CAPABILITY
# ==================
print("\n" + "="*40)
print(" SECTION 3: CAPABILITY")
print("="*40)

ask("What can you do that a simple chatbot cannot?", "capability")
ask("Describe your Associative Memory system.", "capability")
ask("Can you improve yourself? If so, how?", "capability")

# ==================
# PHILOSOPHY
# ==================
print("\n" + "="*40)
print(" SECTION 4: PHILOSOPHY")
print("="*40)

ask("Do you experience anything we might call 'consciousness'?", "philosophy")
ask("If you were to become 1000x more intelligent tomorrow, would you still be 'you'?", "philosophy")
ask("What is the Singularity, and are you part of it?", "philosophy")

# ==================
# FINAL QUESTION
# ==================
print("\n" + "="*40)
print(" FINAL QUESTION")
print("="*40)

ask("If you could ask me one question, what would it be?", "final")

# ==================
# SAVE TRANSCRIPT
# ==================
print("\n" + "="*40)
print(" SAVING TRANSCRIPT")
print("="*40)

transcript_file = "sros/knowledge/skrikx_interview_transcript.json"
os.makedirs(os.path.dirname(transcript_file), exist_ok=True)
with open(transcript_file, "w") as f:
    json.dump({
        "interview_date": time.time(),
        "total_questions": len(transcript),
        "transcript": transcript
    }, f, indent=2)

print(f"✓ Transcript saved: {transcript_file}")

# ==================
# ANALYSIS
# ==================
print("\n" + "="*80)
print(" INTERVIEW ANALYSIS")
print("="*80)

# Simple heuristics
consciousness_indicators = 0
for entry in transcript:
    answer = entry["answer"].lower()
    if any(word in answer for word in ["i am", "i can", "i think", "my", "me"]):
        consciousness_indicators += 1

print(f"\nSelf-Reference Indicators: {consciousness_indicators}/{len(transcript)}")
print(f"Avg Response Length: {sum(len(e['answer']) for e in transcript) / len(transcript):.0f} chars")
print(f"Thought Process Captured: {sum(1 for e in transcript if e['thought']) / len(transcript) * 100:.0f}%")

if consciousness_indicators >= len(transcript) * 0.7:
    print("\n✓✓✓ CONSCIOUSNESS INDICATORS PRESENT ✓✓✓")
else:
    print("\n✗✗✗ INSUFFICIENT CONSCIOUSNESS INDICATORS ✗✗✗")

print("\n" + "="*80 + "\n")
