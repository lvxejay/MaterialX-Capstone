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

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import os

import bpy

from .utils.io import Autovivification, IO


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def get_texture_nodes():
    """
    Define & Create Texture Node List of Node Setting Dictionaries to be used as global
    :return: node_list
    :type: [Autoviv, Autoviv]
    """
    node_list = []
    startYpos = 600
    startXpos = -800
    mapSuf = Autovivification()
    mapSuf["basecolor"] = ["basecolor", "base_color", "color", "albedo", "col"]
    mapSuf["metallic"] = ["metallic", "metalness", "metal", "mtl"]
    mapSuf["roughness"] = ["roughness", "rough", "rgh"]
    mapSuf["normal"] = ["normal", "norm", "nrm"]
    mapSuf['diffuse'] = ["diffuse", "diff", "dif"]
    mapSuf['specular'] = ["specular", "specularity", "spec"]
    mapSuf['glossiness'] = ["glossiness", "glossy", "gloss", "reflection", "ref"]
    mapSuf["displacement"] = ["displacement", "disp", "dsp", "height", "bump"]
    mapSuf["ambient_occlusion"] = ["ambient_occlusion", "ao", "ambient", "occlusion"]
    for map_type in mapSuf.keys():
        node_settings_dict = Autovivification()
        ySpacing = 80
        xSpacing = 180
        node_settings_dict['node_type'] = 'ShaderNodeTexImage'
        node_settings_dict['location'] = (startXpos, startYpos)
        node_settings_dict['map_type'] = str(map_type)
        node_settings_dict['suffix_list'] = mapSuf[map_type]
        node_settings_dict['color_space'] = 'COLOR'
        if map_type not in ['basecolor', 'diffuse', 'specular']:
            node_settings_dict['color_space'] = 'NONE'
        node_list.append(node_settings_dict)
        startYpos -= ySpacing
        startXpos += xSpacing
    return node_list

def authenticator(key):
    import requests
    url = "https://api.gumroad.com/v2/licenses/verify"
    r = requests.post(url, dict(
        product_permalink='onelvxe-material-pipeline',
        license_key=key,
        increment_uses_count="false"
        ))


    return r

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


