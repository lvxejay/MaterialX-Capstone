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

try:
    import MaterialX as mx
except ImportError:
    mx = None
    print("MaterialX extend_cycles_nodes.py module could not load MaterialX library")

# Standard Imports
import sys
import inspect
import os
import platform

# Standard Blender Python API imports
import bpy
from bpy.props import *
import mathutils

from ...utils.io import IO, Autovivification
from .materialx_network import MaterialXNetwork
# Node Extensions
from . import extend_cycles_nodes as ext_cycles #cycles
from . import extend_prman_nodes as ext_prman #renderman
ext_arnold = None #arnold
ext_rs = None #redshift
ext_vray = None #vray

# Classes defined in this module
# mod_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
# # Pulls Custom Cycles Classes from the list of classes in this module
# cycles_custom_classes = [str(x[0]).rsplit('_', 1)[1] for x in mod_classes if
#                          'CMCN_' in x[0]]
# prman_custom_classes = [str(x[0]).rsplit('_', 1)[1] for x in mod_classes if
#                          'RMCN_' in x[0]]

class_dict = {
    'CYCLES'    : 'CMCN', #cycles
    'PRMAN'     : 'RMCN', #renderman
    'ARNOLD'    : 'ARCN', #arnold
    'VRAY'      : 'VRCN', #vray
    'RS'        : 'RSCN', #redshift
              }


cycles_node_string = [
    "ShaderNodeAddShader, ShaderNodeAmbientOcclusion, ShaderNodeAttribute, "
    "ShaderNodeBackground, ShaderNodeBlackbody, ShaderNodeBrightContrast, "
    "ShaderNodeBsdfAnisotropic, ShaderNodeBsdfDiffuse, ShaderNodeBsdfGlass, "
    "ShaderNodeBsdfGlossy, ShaderNodeBsdfHair, ShaderNodeBsdfPrincipled, "
    "ShaderNodeBsdfRefraction, ShaderNodeBsdfToon, ShaderNodeBsdfTranslucent, "
    "ShaderNodeBsdfTransparent, ShaderNodeBsdfVelvet, ShaderNodeBump, "
    "haderNodeCameraData, ShaderNodeCombineHSV, ShaderNodeCombineRGB, "
    "ShaderNodeCombineXYZ, ShaderNodeEmission, ShaderNodeExtendedMaterial, "
    "ShaderNodeFresnel, ShaderNodeGamma, ShaderNodeGeometry, ShaderNodeGroup, "
    "ShaderNodeHairInfo, ShaderNodeHoldout, ShaderNodeHueSaturation, "
    "ShaderNodeInvert, ShaderNodeLampData, ShaderNodeLayerWeight, "
    "ShaderNodeLightFalloff, ShaderNodeLightPath, ShaderNodeMapping, "
    "ShaderNodeMaterial, ShaderNodeMath, ShaderNodeMixRGB, ShaderNodeMixShader, "
    "ShaderNodeNewGeometry, ShaderNodeNormal, ShaderNodeNormalMap, "
    "ShaderNodeObjectInfo,"
    "ShaderNodeParticleInfo, ShaderNodeRGB, ShaderNodeRGBCurve, ShaderNodeRGBToBW, "
    "ShaderNodeScript, ShaderNodeSeparateHSV, ShaderNodeSeparateRGB, "
    "ShaderNodeSeparateXYZ, ShaderNodeSqueeze, ShaderNodeSubsurfaceScattering, "
    "ShaderNodeTangent, ShaderNodeTexBrick, ShaderNodeTexChecker, "
    "ShaderNodeTexCoord, ShaderNodeTexEnvironment, ShaderNodeTexGradient, "
    "ShaderNodeTexImage, ShaderNodeTexMagic, ShaderNodeTexMusgrave, "
    "ShaderNodeTexNoise, ShaderNodeTexPointDensity, ShaderNodeTexSky, "
    "ShaderNodeTexVoronoi, ShaderNodeTexWave, ShaderNodeTexture, "
    "ShaderNodeUVAlongStroke, ShaderNodeUVMap, ShaderNodeValToRGB, "
    "ShaderNodeValue, ShaderNodeVectorCurve, ShaderNodeVectorMath, "
    "ShaderNodeVectorTransform, ShaderNodeVolumeAbsorption, "
    "ShaderNodeVolumeScatter, ShaderNodeWavelength, ShaderNodeWireframe"]

cycles_nodes = {x.strip(" ") for x in cycles_node_string[0].split(',')}
prman_node_list = ['PxrOSLPatternNode', 'PxrSeExprPatternNode',
                   'PxrBlackBodyPatternNode', 'PxrBlendPatternNode',
                   'PxrCheckerPatternNode',
                   'PxrClampPatternNode', 'PxrColorCorrectPatternNode',
                   'PxrExposurePatternNode', 'PxrGammaPatternNode', 'PxrHSLPatternNode',
                   'PxrHairColorPatternNode', 'PxrInvertPatternNode',
                   'PxrLayeredBlendPatternNode',
                   'PxrMixPatternNode', 'PxrProjectionStackPatternNode',
                   'PxrRampPatternNode',
                   'PxrRemapPatternNode', 'PxrThinFilmPatternNode',
                   'PxrThresholdPatternNode',
                   'PxrVaryPatternNode', 'PxrBlackBxdfNode', 'PxrConstantBxdfNode',
                   'PxrDiffuseBxdfNode', 'PxrDisneyBxdfNode', 'PxrGlassBxdfNode',
                   'PxrHairBxdfNode', 'PxrLayerSurfaceBxdfNode',
                   'PxrLightEmissionBxdfNode',
                   'PxrMarschnerHairBxdfNode', 'PxrSkinBxdfNode', 'PxrSurfaceBxdfNode',
                   'PxrVolumeBxdfNode', 'PxrMeshLightLightNode',
                   'PxrAttributePatternNode',
                   'PxrGeometricAOVsPatternNode', 'PxrMatteIDPatternNode',
                   'PxrPrimvarPatternNode', 'PxrShadedSidePatternNode',
                   'PxrTeePatternNode',
                   'PxrToFloatPatternNode', 'PxrToFloatPatternNode',
                   'PxrToFloat3PatternNode',
                   'PxrVariablePatternNode', 'PxrBumpManifold2DPatternNode',
                   'PxrManifold2DPatternNode', 'PxrManifold3DPatternNode',
                   'PxrManifold3DNPatternNode', 'PxrProjectorPatternNode',
                   'PxrRandomTextureManifoldPatternNode', 'PxrRoundCubePatternNode',
                   'PxrTileManifoldPatternNode', 'PxrBakePointCloudPatternNode',
                   'PxrBakeTexturePatternNode', 'PxrDirtPatternNode',
                   'PxrFractalPatternNode',
                   'PxrLayeredTexturePatternNode', 'PxrFractalizePatternNode',
                   'PxrMultiTexturePatternNode', 'PxrProjectionLayerPatternNode',
                   'PxrPtexturePatternNode', 'PxrTexturePatternNode',
                   'PxrVoronoisePatternNode', 'PxrWorleyPatternNode',
                   'PxrDisplaceDisplacementNode', 'PxrAdjustNormalPatternNode',
                   'PxrBumpPatternNode', 'PxrFlakesPatternNode',
                   'PxrNormalMapPatternNode',
                   'aaOceanPrmanShaderPatternNode', 'PxrCrossPatternNode',
                   'PxrDotPatternNode',
                   'PxrFacingRatioPatternNode', 'PxrTangentFieldPatternNode',
                   'PxrDispScalarLayerPatternNode', 'PxrDispTransformPatternNode',
                   'PxrDispVectorLayerPatternNode', 'PxrLayerPatternNode',
                   'PxrLayerMixerPatternNode']
prman_nodes = {x for x in prman_node_list}
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def get_custom_classes(module_name, class_prefix):
    classes = inspect.getmembers(module_name, inspect.isclass)
    custom_classes = [str(x[0]).rsplit('_', 1)[1] for x in classes if
                         '%s_'%(class_prefix) in x[0]]
    return custom_classes


def get_custom_module(prefix):
    if prefix == 'CMCN':
        return ext_cycles
    elif prefix == 'RMCN':
        return ext_prman
    elif prefix == 'ARCN':
        return ext_arnold
    elif prefix == 'VRCN':
        return ext_vray
    elif prefix == 'RSCN':
        return ext_rs

def yield_custom_modules():
    yield from [
            (ext_cycles, 'CMCN'),
            (ext_prman, 'RMCN'),
            (ext_arnold, 'ARCN'),
            (ext_vray, 'VRCN'),
            (ext_rs, 'RSCN'),
        ]

def get_mtlx_data(node):
    """
    Getter function for Blender Nodes that returns a class instance of that node's
    respective custom class
    Args:
        node: Blender Node
    Returns:
        ClassInstance()
    """
    # Get the Node's Blender idname for comparison to custom class name
    id_name = node.bl_idname
    class_type = node.render_engine #CHECK MTLX_DATA FOR THIS
    if class_type:
        if class_type in class_dict.keys():
            cls_prefix = str(class_dict[class_type])
            cls_module = get_custom_module(cls_prefix)
            module_name = cls_module
            custom_classes = get_custom_classes(module_name, cls_prefix)
            if any(id_name in x for x in custom_classes):
                # Look for the matching class in this module
                cls_name = "%s_%s" % (cls_prefix, str(id_name))
                IO.info("MaterialX Node Data; IDNAME: %s" % cls_name)
                # current_module = sys.modules[cls_module]
                dynamic_class = getattr(cls_module, cls_name)
                # Create and return an instance of that class
                instance = dynamic_class(node)
                return instance
            elif not any(id_name in x for x in custom_classes):
                if 'Output' in id_name:
                    return None
                class_list = getattr(cls_module, 'class_list')
                if any(id_name in x for x in class_list):
                    # Look for the matching class in this module
                    cls_name = "%s_%s" % (cls_prefix, str(id_name))
                    IO.info("MaterialX Node Data; IDNAME: %s" % cls_name)
                    # current_module = sys.modules[cls_module]
                    dynamic_class = getattr(cls_module, cls_name)
                    # Create and return an instance of that class
                    instance = dynamic_class(node)
                    return instance
    else:
        return None


def get_node_class_name(idname, **kwargs):
    """Getter for the node class name of a nodedef idname parsed from a MTLX doc"""
    cls_prefix = kwargs.get('class_type', None)
    if cls_prefix is None:
        for cls_module, prefix in yield_custom_modules(): # yield mods and prefixes
            for name in get_custom_classes(cls_module, prefix):
                if name.lower() == idname:
                    return name
    else:
        cls_module = get_custom_module(cls_prefix)
        for name in get_custom_classes(cls_module, cls_prefix):
            if name.lower() == idname:
                return name

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#




def register():
    """Blender's register function. Injects methods and classes into Blender"""
    bpy.types.Node.mtlx_data = get_mtlx_data
    bpy.types.Node.render_engine = StringProperty() #TODO: REMOVE THIS
    bpy.types.NodeSocket.mtlx_name = StringProperty(name='MTLX Name',
                                                    description='Unique MTLX Socket Name')

def unregister():
    """Blender's unregister function. Removes methods and classes from Blender"""
    del bpy.types.Node.mtlx_data
    del bpy.types.NodeSocket.mtlx_name