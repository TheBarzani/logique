with import <nixpkgs> { };

let
  # Import our custom pip derivation that has Python 3.10 compatibility fixes
  customPip = python310Packages.callPackage ./default.nix { };
  
  pythonPackages = python310Packages.override {
    overrides = self: super: {
      # Use our custom pip derivation instead of the broken one
      pip = customPip;
    };
  };
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # Keep all your existing dependencies
    pkgs.stdenv.cc.cc.lib
    git-crypt
    pythonPackages.python
    # pythonPackages.ipykernel
    # pythonPackages.pyzmq
    pythonPackages.venvShellHook
    pythonPackages.pip
    pythonPackages.numpy
    pythonPackages.pandas
    pythonPackages.requests
    pythonPackages.networkx
    pythonPackages.matplotlib
    # Remove pkgconfig as it might be pulling in sphinx
    # pythonPackages.pkgconfig
    # Add build dependencies
    pythonPackages.setuptools
    pythonPackages.wheel
    # pythonPackages.scikit-build
    pkgs.cmake
    pkgs.ninja
    pkgs.pkg-config
    # C++ specific tools needed for compilation
    pkgs.gcc
    pkgs.gnumake
    # System libraries
    taglib
    openssl
    git
    libxml2
    libxslt
    libzip
    zlib
  ];
  
  # Fix for C++ library loading issues
  shellHook = ''
    # Make libraries available to the Python environment
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
    
    # Make sure both your local package and the venv packages are accessible
    export PYTHONPATH="$PWD:$PWD/${venvDir}/lib/python3.10/site-packages:$PYTHONPATH"
    export PYTHONPATH="./tweedledum/python:$PYTHONPATH"

  '';

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    
    python -m ipykernel install --user --name=myenv4 --display-name="myenv4"
    
    # Install base packages first
    pip install --upgrade pip setuptools wheel
    pip install cmake ninja scikit-build
    
    # Install other packages directly
    pip install networkx matplotlib numpy
  '';

  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
    
    # Print environment info for debugging
    echo "Python path: $(which python)"
    echo "PYTHONPATH: $PYTHONPATH"
    echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
  '';
}