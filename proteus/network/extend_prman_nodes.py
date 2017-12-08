# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    Extends Renderman Material Nodes through Blender's Python API.

:description:
    This module extends Cycles Material Nodes through Blender's Python API.
    
    All nodes inherit from MtlxCustomNode()

    Public variabales collect information about the current node, it's sockets
    connections, and parameters. 
    
    Public methods operate on the public variables, and allow users to create, instance,
    define, and modify nodes within MTLX documents.

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
# MaterialX Import. Run in a try statement to ensure MaterialX is installed in the appli-
# cation's python directory.
try:
    import MaterialX as mx
except ImportError:
    mx = None
    print("MaterialX extend_cycles_nodes.py module could not load MaterialX library")


# Standard Blender Python API imports
import bpy
from bpy.props import *
from .base_extensions import MtlxCustomNode

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#


# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class PrmanMtlxCustomNode(MtlxCustomNode):
    """
    Base Cycles MTLX Node Class
    """
    def __init__(self, node):
        super().__init__(node)
        # Private Var Overrides
        self._mtlx_node = self.get_mtlx_node_label() # the mtlx_node name
        self._mtlx_target = 'renderman'

    '''-----------------------------------METHODS--------------------------------------'''

    @property
    def params(self):
        #TODO: Update this so it captures all params
        return self.get_param_keys()

    def get_param_keys(self):
        if hasattr(self.node, 'bl_rna.prop_meta'):
            return sorted(self.node.bl_rna.prop_meta.keys())
        else: return []


    def get_mtlx_node_label(self):
        from .materialx_network import StringResolver
        return StringResolver.normalize_camel_case(self.node.bl_label)

    '''--------------------------Node Property API-------------------------------------'''



class RMCN_PxrOSLPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)


class RMCN_PxrSeExprPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBlackBodyPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBlendPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrCheckerPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrClampPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrColorCorrectPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrExposurePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrGammaPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrHSLPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrHairColorPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrInvertPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrLayeredBlendPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrMixPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrProjectionStackPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrRampPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrRemapPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrThinFilmPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrThresholdPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrVaryPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBlackBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrConstantBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDiffuseBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDisneyBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrGlassBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrHairBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrLayerSurfaceBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrLightEmissionBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrMarschnerHairBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrSkinBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrSurfaceBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrVolumeBxdfNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrMeshLightLightNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrAttributePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrGeometricAOVsPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrMatteIDPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrPrimvarPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrShadedSidePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrTeePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrToFloatPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrToFloat3PatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrVariablePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBumpManifold2DPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrManifold2DPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrManifold3DPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrManifold3DNPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrProjectorPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrRandomTextureManifoldPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrRoundCubePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrTileManifoldPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBakePointCloudPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBakeTexturePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDirtPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrFractalPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrLayeredTexturePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrFractalizePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrMultiTexturePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)


class RMCN_PxrProjectionLayerPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)


class RMCN_PxrPtexturePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrTexturePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrVoronoisePatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrWorleyPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDisplaceDisplacementNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrAdjustNormalPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrBumpPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrFlakesPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrNormalMapPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_aaOceanPrmanShaderPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrCrossPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDotPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrFacingRatioPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrTangentFieldPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDispScalarLayerPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDispTransformPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrDispVectorLayerPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrLayerPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)

class RMCN_PxrLayerMixerPatternNode(PrmanMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)








































