# MaterialX - Blender



[![License](https://www.gnu.org/graphics/gplv3-88x31.png)](https://gitlab.com/lvxejay/materialx-blender/LICENSE.md)


### Repository

The MaterialX - Blender repository consists of the following packages:

    proteus - An implementation of MaterialX in Blender using the MaterialX specification and schema
    setup   - Installation protocol for MaterialX for Blender
    icons   - Icons for MaterialX and Render Engines
    lib     - Python 3 compiled MaterialX Libraries
    test    - Tests and example files
    
    
### Documentation
http://materialx-blender-docs.readthedocs.io/en/latest/index.html    

##### Developers:
Please reference the Developer's Guide in the Documentation for information on how to contribute to and extend this implementation.

###### Contributing:
1) Fork this repository
2) Change features or extend this repository's functionality
3) Create a pull request to integrate your modifications into the repository
4) Wait for your pull request to be accepted.

---

## MaterialX

MaterialX is an open standard for transfer of rich material and look-development content between applications and renderers.  Originated at Lucasfilm in 2012, MaterialX has been used by Industrial Light & Magic (ILM) in feature films such as _Star Wars: The Force Awakens_ and real-time experiences such as _Trials on Tatooine_, and it remains the central material format for new ILM productions.

### Quick Start for Developers

- Download the latest version of the [CMake](https://cmake.org/) build system.
- Point CMake to the root of the MaterialX library (found here: https://github.com/materialx/MaterialX) and generate C++ projects for your platform and compiler.
- Select the `MATERIALX_BUILD_PYTHON` option to build Python 2.x bindings.
- Set the `MATERIALX_PYTHON_EXECUTABLE` and related options to point to Python 3.x files to build Python 3 bindings.'

### Supported Platforms

The MaterialX codebase requires a compiler with support for C++11, and can be built with any of the following:

- Microsoft Visual Studio 2015 or newer
- GCC 4.8 or newer
- Clang 3.3 or newer

The Python bindings for MaterialX are based on [PyBind11](https://github.com/pybind/pybind11), and currently support Python 2.6.x and Python 2.7.x. Python 3.5.x support is considered experimental at this stage.

---
