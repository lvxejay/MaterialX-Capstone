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
import bpy
from bpy.props import *
from ...base_types.base_node import CustomCyclesNode, GroupNodeStruct
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from ....utils.io import IO
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#





class CustomShaderNode_MDL(bpy.types.NodeCustomGroup, CustomCyclesNode):
    bl_idname ='CustomShaderNode_MDL'
    bl_label = "MDL"

    _node_tree_name = 'surface'
    _node_tree_type = 'ShaderNodeTree'
    _node_tree_ext  = ".mdl"

    node_list = [
        ('ShaderNodeBsdfDiffuse', {
            'name': "Diffuse"}),

        ('ShaderNodeBsdfGlossy', {
            'name': 'Glossy',
            'distribution': 'GGX',
            'inputs[1].default_value': 0.25}),

        ('ShaderNodeFresnel', {
            "name": "Fresnel"}),

        ('ShaderNodeMixShader', {
            "name": "Mix",
            "inputs[0].default_value": 1.50}),
    ]

    socket_interface = [
        ("Input", 'NodeSocketFloat', 'Mix'),
        ("Input", "NodeSocketColor", 'Surface Color'),
        ('Input', "NodeSocketFloat", 'Roughness'),
        ('Output', "NodeSocketShader", "Surface"),
    ]

    node_map = [
        ('nodes["group_input"].outputs[0]',
         'nodes["Mix"].inputs[0]'),
        ('nodes["group_input"].outputs[1]',
         'nodes["Diffuse"].inputs[0]'),
        ('nodes["group_input"].outputs[2]',
         'nodes["Glossy"].inputs[1]'),

        ('nodes["group_output"].inputs[0]',
         'nodes["Mix"].outputs[0]'),

        ('nodes["Mix"].inputs[0]',
         'nodes["Fresnel"].outputs[0]'),
        ('nodes["Mix"].inputs[1]',
         'nodes["Diffuse"].outputs[0]'),
        ('nodes["Mix"].inputs[2]',
         'nodes["Glossy"].outputs[0]'),
    ]

    def create_node_tree(self, node_tree_name, node_dict):
        """Create the node tree we are instantiating into the Node Group"""
        self.node_tree = bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree')
        custom_group = GroupNodeStruct(node_list=self.node_list)
        custom_group.socket_interface = self.socket_interface
        custom_group.node_map = self.node_map
        self.add_node('NodeGroupInput', {'name': 'group_input'})
        self.add_node('NodeGroupOutput', {'name': 'group_output'})
        node_dict = self.node_dict

        # Add All Nodes
        IO.info('Node List')
        IO.debug(self.node_list)
        for node in custom_group.node_list:
            self.add_node(node[0], node[1])
        # Add Sockets
        IO.info('Socket Set')
        IO.debug(self.socket_interface)
        for socket in custom_group.socket_interface:
            self.add_socket(socket[0], socket[1], socket[2])
        # Add Links
        IO.info('Node Map')
        IO.debug(self.node_map)
        for link in custom_group.node_map:
            self.inner_link(link[0], link[1])



class ExtraNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == 'ShaderNodeTree' and
                context.scene.render.use_shading_nodes)


node_categories = [
    ExtraNodesCategory("SH_MDL_NODES", "MDL Nodes", items=[NodeItem("CustomShaderNode_MDL")]
    ),

    ]

def register():
    nodeitems_utils.register_node_categories("SH_MDL_NODES", node_categories)



def unregister():
    nodeitems_utils.unregister_node_categories("SH_MDL_NODES")

