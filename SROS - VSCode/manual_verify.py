import sys
import os

# Add repo root to path
sys.path.append(os.path.abspath("sros_v1"))

from tests.sros_test_suite import TestSROSIntegration

def run():
    print("Running SROS Manual Verification...")
    test = TestSROSIntegration()
    
    # Mock fixture behavior
    from sros.kernel import kernel_bootstrap
    kernel = kernel_bootstrap.boot("sros_v1/sros_config.yml")
    
    try:
        test.test_full_stack_flow(kernel)
        test.test_governance_audit(kernel)
        print("\n[SUCCESS] All SROS v1 systems verified.")
    except Exception as e:
        print(f"\n[FAILURE] Verification failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kernel.registry.stop_all()

if __name__ == "__main__":
    run()
