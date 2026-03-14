"""
ASI Integration Validation Test
================================

Validates all ASI upgrades:
1. Azure GPT-5 integration
2. Response caching
3. Parallel executor
4. Batch processor
5. SkrikxAgent integrity
"""
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_azure_gpt5_config():
    """Test Azure GPT-5 environment configuration."""
    logger.info("=" * 60)
    logger.info("TEST 1: Azure GPT-5 Configuration")
    logger.info("=" * 60)
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT"
    ]
    
    missing = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"✓ {var}: {'*' * 10} (set)")
        else:
            logger.error(f"✗ {var}: MISSING")
            missing.append(var)
    
    if missing:
        logger.error(f"FAILED: Missing {len(missing)} required variables")
        return False
    
    logger.info("PASSED: Azure GPT-5 configuration complete")
    return True

def test_model_router():
    """Test ModelRouter with Azure GPT-5."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Model Router Azure GPT-5 Integration")
    logger.info("=" * 60)
    
    try:
        from sros.models.model_router import ModelRouter
        
        router = ModelRouter()
        
        # Check backend availability
        backends = router.get_available_backends()
        logger.info(f"Available backends: {backends}")
        
        if "azure_gpt5" in backends:
            logger.info("✓ Azure GPT-5 backend available")
        else:
            logger.warning("✗ Azure GPT-5 backend not available")
            return False
        
        # Test cache
        if hasattr(router, '_response_cache'):
            logger.info("✓ Response cache initialized")
        else:
            logger.error("✗ Response cache missing")
            return False
        
        logger.info("PASSED: Model Router integration complete")
        return True
        
    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False

def test_parallel_executor():
    """Test Parallel Executor."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Parallel Executor")
    logger.info("=" * 60)
    
    try:
        from sros.runtime.parallel_executor import ParallelExecutor
        
        executor = ParallelExecutor(max_workers=5)
        
        # Test parallel execution
        def task(x):
            return x * 2
        
        tasks = [lambda i=i: task(i) for i in range(10)]
        results = executor.execute(tasks)
        
        # Sort results since parallel execution doesn't guarantee order
        results_sorted = sorted(results)
        expected = [i * 2 for i in range(10)]
        
        if results_sorted == expected:
            logger.info(f"✓ Parallel execution: {len(results)} tasks completed")
            logger.info("PASSED: Parallel Executor functional")
            return True
        else:
            logger.error(f"✗ Results mismatch: {results_sorted} != {expected}")
            return False
            
    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False

def test_batch_processor():
    """Test Batch Processor."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Batch Processor")
    logger.info("=" * 60)
    
    try:
        from sros.runtime.batch_processor import BatchProcessor
        
        processor = BatchProcessor(batch_size=3)
        
        # Test batch processing
        items = list(range(10))
        
        def batch_func(batch):
            return [x * 2 for x in batch]
        
        results = processor.process(items, batch_func)
        expected = [i * 2 for i in range(10)]
        
        if results == expected:
            logger.info(f"✓ Batch processing: {len(results)} items processed")
            logger.info("PASSED: Batch Processor functional")
            return True
        else:
            logger.error(f"✗ Results mismatch: {results} != {expected}")
            return False
            
    except Exception as e:
        logger.error(f"FAILED: {e}")
        return False

def test_skrikx_agent():
    """Test SkrikxAgent integrity."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: SkrikxAgent Integrity")
    logger.info("=" * 60)
    
    try:
        from sros.runtime.agents.skrikx_agent import SkrikxAgent
        
        # Check class exists and has critical methods
        methods = [
            'chat', 'think', 'plan', 'critique', 'refine', 'act',
            'verify', 'evolve', 'diagnose', 'self_improve_code'
        ]
        
        missing = []
        for method in methods:
            if hasattr(SkrikxAgent, method):
                logger.info(f"✓ Method: {method}")
            else:
                logger.error(f"✗ Missing method: {method}")
                missing.append(method)
        
        if missing:
            logger.error(f"FAILED: Missing {len(missing)} methods")
            return False
        
        # Check imports are working
        logger.info("✓ All imports successful")
        logger.info("✓ Class definition valid")
        
        logger.info("PASSED: SkrikxAgent integrity verified")
        return True
        
    except Exception as e:
        logger.error(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    logger.info("\n" + "=" * 60)
    logger.info("ASI INTEGRATION VALIDATION SUITE")
    logger.info("=" * 60 + "\n")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        ("Azure GPT-5 Config", test_azure_gpt5_config),
        ("Model Router", test_model_router),
        ("Parallel Executor", test_parallel_executor),
        ("Batch Processor", test_batch_processor),
        ("SkrikxAgent", test_skrikx_agent),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("=" * 60)
    logger.info(f"RESULT: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    logger.info("=" * 60)
    
    if passed_count == total_count:
        logger.info("\n🎉 ASI INTEGRATION: VERIFIED")
        return 0
    else:
        logger.error(f"\n❌ ASI INTEGRATION: FAILED ({total_count - passed_count} tests failed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
