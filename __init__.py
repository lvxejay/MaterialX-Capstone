# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber


:synopsis:
    MaterialXBlender is a reference implementation of the MaterialX Specification
    developed by ILM with contributions from Autodesk and The Foundry.

:description:


:applications:
    Blender 3D

:see_also:


:license:
    see LICENSE.md
"""

bl_info = {
    "name": "MaterialXBlender",
    "author": "Jared Webber - Blender One",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Material",
    "description": "",
    "category": "Material",
    "tracker_url": "https://gitlab.com/lvxejay/materialx-blender/issues",
    # "support": "TESTING",
    "wiki_url": "http://materialx-blender-docs.readthedocs.io/en/latest/index.html"
}

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import os
from . import conf
from . utils.io import IO

# Check for Blender
try:
    import bpy
except ImportError:
    pass

try:
    from .setup import developer_utils
except ImportError:
    pass

if "developer_utils" not in globals():
    message = ("\n\n"
               "MaterialXBlender cannot be registered correctly\n"
               "Troubleshooting:\n"
               "  1. Try installing the addon in the newest official Blender version.\n"
               "  2. Try installing the newest MaterialXBlender version from Gitlab.\n")
    raise Exception(message)

# Import and Reload Submodules
import importlib
from .setup import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def install_materialx():
    """Installs MaterialX into a Blender's Python Site Packages"""

    import shutil
    import platform

    # Get Resource and User Paths for installing lib into the user's blender installation
    resource_path = bpy.utils.resource_path('LOCAL', major=bpy.app.version[0],
                                            minor=bpy.app.version[1])
    user_path = bpy.utils.resource_path('USER', major=bpy.app.version[0],
                                        minor=bpy.app.version[1])
    local_path = resource_path
    bpy_dir = os.path.join(resource_path, 'python')
    config_dir = os.path.join(user_path, 'scripts/config')

    # Climb up path
    uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
    addon_path = os.path.dirname(__file__)
    # Library Directory
    dist_dir = os.path.join(addon_path, "lib", 'dist')

    # Windows
    if platform.system() == 'Windows':
        IO.info("OS Type: Windows. Installing MaterialX for Windows 10")
        mtlx_lib = os.path.join(dist_dir, 'win', 'MaterialX.zip')
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        # Check for Admin Privileges
        if is_admin != 1:
            IO.error("Cannot Install MaterialX. Run Blender as an Administrator")
        # Unpack the library to the blender installation from config
        site_packages = os.path.join(bpy_dir, 'lib', 'site-packages')
        shutil.unpack_archive(mtlx_lib, site_packages)
        IO.info("MaterialX unpacked and installed here: %s" % site_packages)

    # OSX
    elif platform.system() == 'darwin':
        IO.info("OS Type: OSX. Material Pipeline currently unsupported.")
        pass
        # TODO: Unpack the library to the blender installation from config

    # Linux
    elif platform.system() == 'linux':
        IO.info("OS Type: Linux. Installing MaterialX for Linux")
        mtlx_lib = os.path.join(dist_dir, 'linux', 'MaterialX.tar.xz')
        site_packages = os.path.join(bpy_dir, 'lib', 'python3.5', 'site-packages')
        shutil.unpack_archive(mtlx_lib, site_packages)
        IO.info("MaterialX unpacked and installed here: %s" % site_packages)

def install_materialx_requirements():
    """Use pip to install requirements.txt reqs."""

    python = bpy.app.binary_path_python # Blender's Python Installation
    cur_dir = os.path.dirname(os.path.realpath(__file__)) # Current directory
    req_file = os.path.join(cur_dir, 'requirements.txt') # requirements file
    # Commmand to install the requirements
    command = [
        python,
        '-m'
        'pip',
        'install',
        "-r", req_file
    ]
    # Install the requirements
    run_command_popen(command)

def run_command_popen(cmd):
    """Method to run a subprocess command using Popen"""

    import subprocess
    sp = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if err:
        print("__________________________")
        print("Subprocess standard error:")
        print(err.decode('ascii'))
        # sp.wait()

def register_addon():
    """Installs or bootstraps pip to install extra libraries"""

    try:
        import pip
    except ImportError:
        IO.info("pip not found. Installing pip.")
        try:
            import ensurepip
            ensurepip.bootstrap(upgrade=True, default_pip=True)
            IO.info("pip installation successful")
        except ImportError:
            IO.info("pip cannot be configured or installed.")

def unregister_addon():
    """
    Blender specific un-register function
    :return:
    """
    IO.info("Unregistered MaterialXBlender")

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#



# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def register():
    """Registers all modules in this addon"""

    register_addon()
    try:
        import MaterialX as mx
        IO.info("MaterialX Library Loaded")
    except ImportError:
        IO.info("MaterialX Library missing. Installing the MaterialX Library")
        install_materialx()

    bpy.utils.register_module(__name__)
    for module in modules:
        if hasattr(module, "register"):
            module.register()

    # Register Blender Properties and Handlers
    conf.register()


def unregister():
    """Unregisters all modules in this addon"""


    bpy.utils.unregister_module(__name__)
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()

    # Unregister Blender Properties and Handlers
    conf.unregister()
    unregister_addon()


# if __name__ == "__main__":
#     register()
# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#







