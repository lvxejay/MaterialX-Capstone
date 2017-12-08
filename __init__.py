

# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber


:synopsis:


:description:


:applications:

:see_also:

:license:
    see license.txt and EULA.txt 

"""
bl_info = {
    "name": "ONELVXE Material Pipeline",
    "author": "Jared Webber",
    "version": (2, 0, 0),
    "blender": (2, 79, 0),
    "location": "Scene UI > Pipeline",
    "description": "",
    "category": "Pipeline",
    "tracker_url": "http://bfy.tw/CD5H",
    "wiki_url": ""
}

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import os
import sys
from . import conf
from . import addon_updater_ops
from . utils.io import IO

# Check for Blender
try:
    import bpy
except ImportError:
    pass

try:
    from .setup import developer_utils
except:pass
if "developer_utils" not in globals():
    message = ("\n\n"
               "Material Pipeline cannot be registered correctly\n"
               "Troubleshooting:\n"
               "  1. Try installing the addon in the newest official Blender version.\n"
               "  2. Try installing the newest Material Pipeline version from Gitlab.\n")
    raise Exception(message)

# Import and Reload Submodules
import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def install_materialx():
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
    if platform.system() == 'Windows':
        IO.info("OS Type: Windows. Installing MaterialX for Windows 10")
        matx_lib = os.path.join(dist_dir, 'win', 'MaterialX.zip')
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        # Check for Admin Privileges
        if is_admin != 1:
            IO.error("Cannot Install MaterialX. Run Blender as an Administrator")
        # Unpack the library to the blender installation from config
        site_packages = os.path.join(bpy_dir, 'lib', 'site-packages')
        shutil.unpack_archive(matx_lib, site_packages)
        IO.info("MaterialX unpacked and installed here: %s" % site_packages)
    elif platform.system() == 'darwin':
        IO.info("OS Type: OSX. Material Pipeline currently unsupported.")
        pass
        # Unpack the library to the blender installation from config
    elif platform.system() == 'linux':
        IO.info("OS Type: Linux. Installing MaterialX for Linux")
        matx_lib = os.path.join(dist_dir, 'linux', 'MaterialX.tar.xz')
        site_packages = os.path.join(bpy_dir, 'lib', 'python3.5', 'site-packages')
        shutil.unpack_archive(matx_lib, site_packages)
        IO.info("MaterialX unpacked and installed here: %s" % site_packages)


def register_addon():
    """
    Blender specific registration function
    :return:
    """
    # Register Blender Properties and Handlers

    try:
        import pip
    except ImportError:
        IO.info("pip python package not found. Installing.")
        try:
            import ensurepip
            ensurepip.bootstrap(upgrade=True, default_pip=True)
        except ImportError:
            IO.info("pip cannot be configured or installed. ")

def unregister_addon():
    """
    Blender specific un-register function
    :return:
    """
    IO.info("Unregistered Material Pipeline")

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#



# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def register():
    """
    Blender specific registration function
    :return: 
    """
    register_addon()
    try:
        import MaterialX as mx
        IO.info("MaterialX Loaded")
    except ImportError:
        IO.info("MaterialX not found. Installing")
        install_materialx()
    bpy.utils.register_module(__name__)
    for module in modules:
        if hasattr(module, "register"):
            module.register()
    # Register Blender Properties and Handlers
    addon_updater_ops.register_updater(bl_info)
    conf.register()


def unregister():
    """
    Blender specific un-register function
    :return: 
    """
    bpy.utils.unregister_module(__name__)
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
    # Unregister Blender Properties and Handlers
    conf.unregister()
    addon_updater_ops.unregister_updater()
    unregister_addon()


# if __name__ == "__main__":
#     register()
# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#







