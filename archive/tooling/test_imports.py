#!/usr/bin/env python3
"""
Test script to verify different import methods for the vcgc package
"""

def test_full_import():
    """Test importing the entire package"""
    print("Testing: import vcgc")
    import vcgc
    
    print(f"  ✓ Package version: {vcgc.__version__}")
    print(f"  ✓ Available classes: {vcgc.__all__}")
    
    # Test instantiation
    network = vcgc.VCPNetwork()
    bf = vcgc.BooleanFunction()
    synth = vcgc.Synthesizer()
    func = vcgc.read_dimacs
    
    print("  ✓ All classes can be instantiated")
    return True

def test_specific_imports():
    """Test importing specific classes"""
    print("\nTesting: from vcgc import ...")
    
    from vcgc import VCPNetwork, BooleanFunction, Synthesizer, read_dimacs
    
    # Test instantiation
    network = VCPNetwork()
    bf = BooleanFunction()
    synth = Synthesizer()
    
    print("  ✓ Specific imports work")
    print("  ✓ Classes can be instantiated")
    return True

def test_module_imports():
    """Test importing individual modules"""
    print("\nTesting: from vcgc.module import ...")
    
    from vcgc.network import VCPNetwork
    from vcgc.boolean import BooleanFunction  
    from vcgc.synthesis import Synthesizer
    from vcgc.dimacs import read_dimacs
    
    # Test instantiation
    network = VCPNetwork()
    bf = BooleanFunction()
    synth = Synthesizer()
    
    print("  ✓ Module-level imports work")
    print("  ✓ Classes can be instantiated")
    return True

def main():
    """Run all import tests"""
    print("=== VCGC Package Import Tests ===\n")
    
    try:
        test_full_import()
        test_specific_imports() 
        test_module_imports()
        
        print("\n=== All tests passed! ===")
        print("The vcgc package is properly configured and ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    main()
