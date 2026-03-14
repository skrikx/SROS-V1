"""
Quick validation script for Phase 1: Gemini integration with agents
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file
from pathlib import Path
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    print(f"✓ Loaded .env file")
else:
    print(f"✗ No .env file found at {env_file}")
    sys.exit(1)

# Verify API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✓ GEMINI_API_KEY loaded (length: {len(api_key)})")
else:
    print("✗ GEMINI_API_KEY not found")
    sys.exit(1)

# Test Architect Agent
print("\n=== Testing Architect Agent ===")
from sros.runtime.agents import ArchitectAgent

agent = ArchitectAgent()
agent.initialize()

if agent.adapter:
    print(f"✓ Adapter initialized: {agent.adapter.name}")
else:
    print("✗ Adapter not initialized")
    sys.exit(1)

# Make a real call
print("\nMaking real Gemini call...")
result = agent.act("Analyze: The kernel event bus is experiencing message delivery delays. What could be the root cause?")

print(f"\n=== Response ===")
print(result[:500])
print(f"\n... (truncated, total length: {len(result)} chars)")

if "[ERROR]" in result:
    print("\n✗ Agent returned error")
    sys.exit(1)
else:
    print("\n✓ Agent successfully called Gemini and returned analysis")

print("\n=== Phase 1 VALIDATED ===")
