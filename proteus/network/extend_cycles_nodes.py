# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    
:synopsis:
    Extends Cycles Material Nodes through Blender's Python API.

:description:
    This module extends Cycles Material Nodes through Blender's Python API.
    
    All nodes inherit from MtlxCustomNode()

    Public variabales collect information about the current node, it's sockets
    connections, and parameters. 
    
    Public methods operate on the public variables, and allow users to create, instance,
    define, and modify nodes within MTLX documents.

:applications:
    Blender 3D
    
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

from .materialx_network import MaterialXNetwork
from .base_extensions import MtlxCustomNode
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#


# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

'''Base Classes: All Custom MTLX Nodes Inherit from here'''

class CyclesMtlxCustomNode(MtlxCustomNode):
    """
    Base Cycles MTLX Node Class
    """
    def __init__(self, node):
        # Superclass CyclesMtlxCustomNode
        super().__init__(node)

        # Set the target for the subclass
        self._mtlx_target = 'cycles'


        '''Must include a mtlx_node_name for every node'''
        # self.mtlx_node = 'mtlx_node_name'

        '''Must include a list of parameters for every node'''
        # self.params = ['param1', 'param2']



class CyclesMtlxCustomNode_Shader(CyclesMtlxCustomNode):
    """Cycles Custom Shader Node Implementation"""
    def __init__(self, node):

        #Superclass CyclesMtlxCustomNode
        super().__init__(node)

        '''Must include a mtlx_node_name for every node'''
        # self.mtlx_node = 'mtlx_node_name'

        '''Must include a list of parameters for every node'''
        # self.params = ['param1', 'param2']

        '''Set the target for the subclass'''
        # self._mtlx_target = 'cycles'



    # MTLX Overrides --------------------------------------------------------------------

    def create_node_def(self, **kwargs):
        """Create a custom node def for this node, overriding the inherited method and
        instead defining a context specific node_def"""

        # Check to see if we already defined this node in the node graph
        if self.defined is True:
            return
        # Query the graph just incase defining this node def was missed
        if self.doc.getNodeDef(self.mtlx_node_def_name) is not None:
            self.defined = True
            return

        # Query API for parameters
        outputs = self.mtlx_outputs
        inputs = self.mtlx_inputs
        parameters = self.mtlx_params
        idname = self.idname
        node_type = self.mtlx_type

        # Create a Custom Node Def for A Custom Shader Node
        shader = self.doc.addNodeDef(name=idname, node=self.mtlx_node,
                                     type='surfaceshader')
        # Set CYCLES Node target
        shader.setTarget('cycles')
        # Create, Inputs, Outputs, and Parameters
        self.create_mtlx_inputs(shader, inputs)
        # self.create_mtlx_outputs(shader, outputs) #Shader Nodes only have 1 output
        self.create_mtlx_parameters(shader, parameters)
        # Set flag to true to avoid duplicate NodeDef creation
        self.defined = True

    def instantiate(self, node_graph):
        """Add this node to the MTLX Node Graph"""

        # Run our pre_instantion setup and definition function
        self.pre_instantiate(node_graph)
        # Grab the Output Sockets of the MaterialX Node Graph
        surf_out = self.mtlx_node_graph.getOutput('ng_surface_out')
        vol_out = self.mtlx_node_graph.getOutput('ng_volume_out')
        disp_out = self.mtlx_node_graph.getOutput('ng_disp_out')

        # Blender Material Output Nodes, MUST have a shader node connceted to them.
        # Any node with a BSDF or Shading type output socket should be queryed for any
        ## connections to the material output node.
        # Connect this node to the node graph output if it's linked in Blender
        for link in self.node_links:
            if link[0] == self.mtlx_name and link[2] == 'material_output':
                if link[3] == 'Surface':
                    surf_out.setNodeName(self.mtlx_graph_node.getName())
                if link[3] == 'Volume':
                    vol_out.setNodeName(self.mtlx_graph_node.getName())
                if link[3] == 'Displacement':
                    disp_out.setNodeName(self.mtlx_graph_node.getName())


#--------------------------------------------------------------------Cycles MTLX Nodes---#

'''----------------------------------------Input Nodes---------------------------------'''

class CMCN_ShaderNodeAttribute(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'attribute' # the name of this node
        self.params = ['attribute_name'] # a list of node parameters

class CMCN_ShaderNodeTangent(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'tangent'
        self.params = ['axis', 'direction_type']

class CMCN_ShaderNodeTexCoord(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'texture_coordinate'
        self.params = ['from_dupli', 'object']

class CMCN_ShaderNodeUVMap(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'uv_map'
        self.params = ['from_dupli', 'uv_map']

class CMCN_ShaderNodeWireframe(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'wireframe'
        self.params = ['use_pixel_size']

class CMCN_ShaderNodeCameraData(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'camera_data'

class CMCN_ShaderNodeNewGeometry(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'geometry'

class CMCN_ShaderNodeHairInfo(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'hair_info'

class CMCN_ShaderNodeLayerWeight(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'layer_weight'

class CMCN_ShaderNodeLightPath(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'light_path'

class CMCN_ShaderNodeObjectInfo(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'object_info'

class CMCN_ShaderNodeParticleInfo(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'particle_info'

class CMCN_ShaderNodeFresnel(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'fresnel'

class CMCN_ShaderNodeRGB(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'rgb'

class CMCN_ShaderNodeValue(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'value'


'''-----------------------------------Shader Nodes-------------------------------------'''

class CMCN_ShaderNodeAddShader(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'add_shader'

class CMCN_ShaderNodeAmbientOcclusion(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'ambient_occlusion'

class CMCN_ShaderNodeBsdfAnisotropic(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'anisostropic_bsdf'
        self.params = ['distribution']

class CMCN_ShaderNodeBsdfDiffuse(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'diffuse_bsdf'

class CMCN_ShaderNodeEmission(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'emission'

class CMCN_ShaderNodeBsdfGlass(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'glass_bsdf'
        self.params = ['distribution']

class CMCN_ShaderNodeBsdfGlossy(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'glossy_bsdf'
        self.params = ['distribution']

class CMCN_ShaderNodeBsdfHair(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'hair_bsdf'
        self.params = ['component']

class CMCN_ShaderNodeHoldout(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'holdout'

class CMCN_ShaderNodeMixShader(CyclesMtlxCustomNode_Shader):
    def __init__(self,   node):
        super().__init__(node)
        self.mtlx_node = 'mix_shader'

class CMCN_ShaderNodeBsdfPrincipled(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'principled_bsdf'
        self.params = ['distribution']

class CMCN_ShaderNodeBsdfRefraction(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'refraction_bsdf'
        self.params = ['distribution']

class CMCN_ShaderNodeSubsurfaceScattering(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'sss_bssdf'
        self.params = ['falloff']

class CMCN_ShaderNodeBsdfToon(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'toon_bsdf'
        self.params = ['component']

class CMCN_ShaderNodeBsdfTranslucent(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'translucent_bsdf'

class CMCN_ShaderNodeBsdfTransparent(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'transparent_bsdf'

class CMCN_ShaderNodeBsdfVelvet(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'velvet_bsdf'

class CMCN_ShaderNodeVolumeAbsorption(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'volume_absorption'

class CMCN_ShaderNodeVolumeScatter(CyclesMtlxCustomNode_Shader):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'volume_scatter'


'''---------------------------------Texture Nodes--------------------------------------'''

#TODO: Need NodeGraph Representations of these nodes to support reads and writes

class CMCN_ShaderNodeTexBrick(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'brick_texture'
        self.params = ['offset', 'offset_frequency', 'squash', 'squash_frequency']

class CMCN_ShaderNodeTexChecker(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'checker_texture'

class CMCN_ShaderNodeTexEnvironment(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        #image, image_user,
        self.mtlx_node = 'environment_texture'
        self.params = ['image', 'color_space', 'interpolation', 'projection']


    def get_node_param(self, node, param):
        if param == 'image':
            param_value = ""
            param_type = 'filename'
            if node.image:
                param_value = str(node.image.filepath)
            return ('image', param_type, param_value)
        else:
            return CyclesMtlxCustomNode.get_node_param(node, param)

class CMCN_ShaderNodeTexGradient(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'gradient_texture'
        self.params = ['gradient_type']

class CMCN_ShaderNodeTexImage(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'image_texture'
        self.params = ['image', 'color_space', 'extension', 'interpolation',
                       'projection', 'projection_blend']

    def get_node_param(self, node, param):
        if param == 'image':
            param_value = ""
            param_type = 'filename'
            if node.image:
                param_value = str(node.image.filepath)
            return ('image', param_type, param_value)


class CMCN_ShaderNodeTexMagic(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'magic_texture'
        self.params = ['turbulence_depth']

class CMCN_ShaderNodeTexMusgrave(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'musgrave_texture'
        self.params = ['musgrave_type']

class CMCN_ShaderNodeTexNoise(CyclesMtlxCustomNode):
    def __init__(self, node):
        self.mtlx_node = 'noise_texture'
        super().__init__(node)

class CMCN_ShaderNodeTexPointDensity(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'point_texture'
        self.params = ['interpolation', 'object', 'particle_color_source',
                       'particle_system', 'point_source', 'radius', 'resolution',
                       'space', 'vertex_attribute_name', 'vertex_color_source']

class CMCN_ShaderNodeTexSky(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'sky_texture'
        self.params = ['ground_albedo', 'sky_type', 'sun_direction', 'turbidity']

class CMCN_ShaderNodeTexVoronoi(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'voronoi_texture'
        self.params = ['coloring']

class CMCN_ShaderNodeTexWave(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'wave_texture'
        self.params = ['wave_profile', 'wave_type']

'''----------------------------------Color Nodes---------------------------------------'''

class CMCN_ShaderNodeBrightContrast(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'bright_contrast'

class CMCN_ShaderNodeGamma(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'gamma'

class CMCN_ShaderNodeHueSaturation(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'hue_saturation'

class CMCN_ShaderNodeInvert(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'invert'

class CMCN_ShaderNodeLightFalloff(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'light_falloff'

class CMCN_ShaderNodeMixRGB(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'mix_rgb'
        self.params = ['blend_type', 'use_alpha', 'use_clamp']

class CyclesCurveNode(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.curve_type = None
        self.curve_bounds = ()

    def get_node_param(self, node, param):
        def get_mapping_points(c_map, c_type):
            c_array = []
            c_dict = {}
            c_set = []

            if c_type == 'color4':
                c_map.initialize() # initialization required by blender
                curves = c_map.curves # get curves
                # Create tupled curve set
                (c, r, g, b) = (('g', curves[0]), ('r',curves[1]),
                                ('b', curves[2]), ('c', curves[3]))
                c_set = [c, r, g, b]

            elif c_type == 'vector3':
                c_map.initialize() # initialization required by blender
                curves = c_map.curves # get curves
                # Create tupled curve set
                x, y, z = ('x', curves[0]), ('y', curves[1]), ('z', curves[2])
                c_set = [x, y, z]
            # Loop through each curve in the set
            for c_c in c_set:
                # Get the curve's points from the curve_map in the list
                c_points = c_c[1].points
                # Get each point's location and put it in an array
                p_array = []
                for point in c_points:
                    point_loc = point.location
                    p_array.append(point_loc.to_tuple(5)) #de-Vectorize
                # Add it to a dict for unpacking later
                c_dict[c_c[0]] = str(p_array[0]).strip("('')")
            return c_dict
        if hasattr(node, param):
            # mapping param is nested, get all the points
            param_value = get_mapping_points(getattr(node,param), self.curve_type)
            param_type = self.curve_type
            param_name = MaterialXNetwork.to_mtlx_name(param)
            if param_type == 'color4':
                value_list = [param_value['c'],
                              param_value['r'],
                              param_value['g'],
                              param_value['b']]
            elif param_type == 'vector3':
                value_list = [param_value['x'],
                              param_value['y'],
                              param_value['z']]
            param_value = value_list
            return (param_name, param_type, str(param_value).strip("['']"))

class CMCN_ShaderNodeRGBCurve(CyclesCurveNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'rgb_curve'
        # self.params = ['mapping']
        self.curve_type = 'color4'

'''--------------------------------------Vector Nodes----------------------------------'''

class CMCN_ShaderNodeMapping(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'mapping'
        self.params = ['max', 'min', 'rotation', 'scale', 'translation',
                       'use_max', 'use_min', 'vector_type']

class CMCN_ShaderNodeBump(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'bump'
        self.params = ['invert']

class CMCN_ShaderNodeNormal(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'normal_node'

class CMCN_ShaderNodeNormalMap(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'normal_map'
        self.params = ['space', 'uv_map']

class CMCN_ShaderNodeVectorTransform(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'vector_transform'
        self.params = ['convert_from', 'convert_to', 'vector_type']

class CMCN_ShaderNodeVectorCurve(CyclesCurveNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'vector_curve'
        # self.params = ['mapping']
        self.curve_type = 'vector3'

'''-------------------------------------Converter Nodes--------------------------------'''

class CMCN_ShaderNodeBlackbody(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'blackbody'

class CMCN_ShaderNodeColorRamp(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'color_ramp'
        self.params = ['color_ramp'] #TODO: Color Ramp Mapping

class CMCN_ShaderNodeCombineHSV(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'combine_hsv'

class CMCN_ShaderNodeCombineRGB(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'combine_rgb'

class CMCN_ShaderNodeCombineXYZ(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'combine_xyz'

class CMCN_ShaderNodeMath(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'math' #TODO: Conditional name based on operation parameter
        self.params = ['operation', 'use_clamp']

class CMCN_ShaderNodeRGBtoBW(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'rgb_bw'

class CMCN_ShaderNodeSeparateHSV(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'separate_hsv'

class CMCN_ShaderNodeSeparateRGB(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'separate_rgb'

class CMCN_ShaderNodeSeparateXYZ(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'separate_xyz'

class CMCN_ShaderNodeVectorMath(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'vector_math'
        self.params = ['operation']

class CMCN_ShaderNodeWavelength(CyclesMtlxCustomNode):
    def __init__(self, node):
        super().__init__(node)
        self.mtlx_node = 'wavelength'


'''Script Nodes''' #Not Implemented

'''Group Nodes''' #TODO: Implement Group Nodes


#-------------------------------------------------------------------------------PRMAN----#



