#!/usr/bin/env python3
"""
IBM Quantum Platform Setup Script
This script configures authentication for IBM Quantum Platform using environment variables.
"""

import os
import sys
from dotenv import load_dotenv

def setup_ibm_quantum():
    """Set up IBM Quantum Platform authentication."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    IBM_QUANTUM_API_TOKEN = os.getenv("IBM_QUANTUM_API_TOKEN")
    INSTANCE_NAME = os.getenv("INSTANCE_NAME")
    
    # Validate that required environment variables are set
    if not IBM_QUANTUM_API_TOKEN:
        print("Error: IBM_QUANTUM_API_TOKEN not found in environment variables.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)
    
    if not INSTANCE_NAME:
        print("Error: INSTANCE_NAME not found in environment variables.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)
    
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        
        # Save account credentials
        QiskitRuntimeService.save_account(
            token=IBM_QUANTUM_API_TOKEN,
            instance=INSTANCE_NAME,
            overwrite=True
        )
        
        print("✓ IBM Quantum Platform credentials saved successfully!")
        
        # Test the connection
        service = QiskitRuntimeService()
        print("✓ Successfully connected to IBM Quantum Platform")
        print(f"✓ Available backends: {len(service.backends())} found")
        
        return True
        
    except ImportError:
        print("Error: qiskit_ibm_runtime not installed.")
        print("Please install it with: pip install qiskit-ibm-runtime")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error setting up IBM Quantum Platform: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Setting up IBM Quantum Platform authentication...")
    setup_ibm_quantum()
    print("Setup complete!")