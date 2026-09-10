"""
Basic tests for the vcgc package
"""
import pytest
import vcgc


def test_package_import():
    """Test that the package can be imported."""
    assert vcgc.__version__ == "0.1.0"
    

def test_main_classes_available():
    """Test that main classes are available after import."""
    assert hasattr(vcgc, 'VCPNetwork')
    assert hasattr(vcgc, 'BooleanFunction')
    assert hasattr(vcgc, 'read_dimacs')
    assert hasattr(vcgc, 'Synthesizer')


def test_vcpnetwork_creation():
    """Test that VCPNetwork can be instantiated."""
    network = vcgc.VCPNetwork()
    assert network is not None


def test_boolean_function_creation():
    """Test that BooleanFunction can be instantiated."""
    bf = vcgc.BooleanFunction()
    assert bf is not None
    assert bf.boolean_function is None


def test_synthesizer_creation():
    """Test that Synthesizer can be instantiated."""
    synth = vcgc.Synthesizer()
    assert synth is not None
    assert synth.logic_network is None
    assert synth.tweedledum_circuit is None
    assert synth.qiskit_circuit is None
