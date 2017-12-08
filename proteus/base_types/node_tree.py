# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    
:synopsis:
    MaterialXNodeTree base NodeTree class definition
    Currently unused, but module was included to be later expanded and implemented

:description:
    The base MaterialXNodeTree that is used to contain the MaterialX Node System
    This module is needed to house all defined nodes and sockets

:applications:
    Blender 3D
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import bpy
from bpy.props import *


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#
# class MaterialXNodeTree(bpy.types.NodeTree):
#     """
#     The Base Node Graph system for MaterialX in Blender
#     """
#     bl_idname = "mx_MaterialXNodeTree"
#     bl_label = "MaterialX"
#     bl_icon = "COLOR"
#     bl_description='The Base Node Graph system for MaterialX in Blender'
#     # Boolean Property to flag if this NodeTree has been saved once
#     saved = BoolProperty()
#     # Global Scene property #TODO: Convert to PointerProperty
#     scene_name = bpy.props.StringProperty(
#         name='Scene',
#         description='The global scene used by this node tree (never none)'
#     )
#
#     @property
#     def scene(self):
#         """Returns the global scene this node tree is active in."""
#         scene = bpy.data.scenes.get(self.scene_name)
#         if scene is None:
#             scene = bpy.data.scenes[0]
#         return scene


# class SocketHandler(object):
#     def __init__(self):
#         self._sockets = None
#         self.socket_map = {}
#         self.socket_names = set()
#
#     def get_sockets(self, node_tree):
#         temp_list = []
#         for node in node_tree.nodes:
#             for input in node.inputs:
#                 temp_list.append(input)
#             for output in node.outputs:
#                 temp_list.append(output)
#         self.sockets = temp_list
#         return self.sockets
#
#     def yield_sockets(self):
#         yield self.sockets
#
#     def create_socket_map(self):
#         for socket in self.yield_sockets():
#             socket_type = None
#             if socket.is_output is False:
#                 socket_type = 'input'
#             elif socket.is_output is True:
#                 socket_type = 'output'
#             socket_tuple = (socket.node.name, socket_type, socket.name, socket.identifier)
#             self.socket_map[socket_tuple] = socket.mtlx_name
#
#     @classmethod
#     def create_socket_tuple(cls, socket):
#         socket_type = cls.get_socket_output_type(socket)
#
#
#     @classmethod
#     def get_socket_output_type(cls, socket):
#         if socket.is_output is False:
#             return 'input'
#         elif socket.is_output is True:
#             return 'output'
#
#     @property
#     def sockets(self):
#         return self._sockets
#     @sockets.setter
#     def sockets(self, socket_list):
#         if isinstance(socket_list, list):
#             self._sockets = socket_list
#         else:
#             self._sockets.append(socket_list)



