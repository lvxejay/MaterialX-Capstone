# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    
:synopsis:
    Configuration file for this addon
    
:description:
    This file defines specific configuration variables and functions for this package.
    The module can be used to house "globals" that need to be shared between modules
    
:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import os
import bpy
from .utils.io import IO

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#


# -----------------------------------------------------------------------------
# ADDON GLOBAL VARIABLES AND INITIAL SETTINGS
# -----------------------------------------------------------------------------

xml_path = ""
xml_load = False

materialx_lib = False
py_reqs = False


#Dynamic Properties:

# -------------------------------------
# verbose print settings

# Enable for verbose printing
v = True
# Enable for very verbose printing
vv = True

# list of active server threads, use for cleanup if needed
server_threads = []
# if set to true, will be used to cancel existing/future threads from starting
threading_halt = False

# -------------------------------------
# Custom icon usage

# default false, icons not supporter till proven supported
use_icons = True
# global collection for custom icons, save different subsets as needed
preview_collections = {}

# function called in register to load icons
def load_icons():
    pcoll_icons = bpy.utils.previews.new()
    # icon path
    icons_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "icons")
    # load a specific icon
    pcoll_icons.load(
        "matx",
        os.path.join(icons_dir, "matx_logo.png"),
        'IMAGE')
    pcoll_icons.load(
        "arnold",
        os.path.join(icons_dir, "arnold_logo.png"),
        'IMAGE')
    pcoll_icons.load(
        "redshift",
        os.path.join(icons_dir, "redshift_logo.png"),
        'IMAGE')
    pcoll_icons.load(
        "renderman",
        os.path.join(icons_dir, "renderman_logo.png"),
        'IMAGE')
    pcoll_icons.load(
        "vray",
        os.path.join(icons_dir, "vray_logo.png"),
        'IMAGE')
    # name one set of general purpose icons
    preview_collections["icons"] = pcoll_icons

# -----------------------------------------------------------------------------
# REGISTRATION
# -----------------------------------------------------------------------------
def register():
    # load_icons()
    # bpy.utils.register_module(__name__)
    # For preview icons
    global use_icons
    try:  # We only need to check this once here
        import bpy.utils.previews
        use_icons = True
    except:
        use_icons = False
    # # load the icons here, only need to do so once
    if use_icons:
        load_icons()

def unregister():
    # bpy.utils.unregister_module(__name__)
    # de-reg/load the pcoll
    # global use_icons, preview_collections
    if use_icons:
        for pcoll in preview_collections.values():
            try:
                bpy.utils.previews.remove(pcoll)
            except ResourceWarning:
                IO.debug("Preview Collection Left Open")
                pass
        preview_collections.clear()


