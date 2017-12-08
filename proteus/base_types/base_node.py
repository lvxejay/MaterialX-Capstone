# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    
:synopsis:
    Base node class definition, methods and functions 

:description:
    This module contains the MaterialXNode class definition. 
    The class has a set of of both private and public methods.
    Private methods generally are not overwritten in any subclasses and are used for
     utility purposes
    Most public methods may be overwritten in subclasses and are listed under the 
    docstring heading. 
    Class Properties also provided for convenience for accessing useful node parameters
    and calling functions to return processed values. 

:applications:
    Blender 3D
    
:see_also:
   ./base_socket.py
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import random

import bpy
from bpy.props import *

from ..properties.dynamic_property import node_parameter

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def create_identifier():
    """Creates a random identifier string."""
    identifierLength = 15
    characters = "abcdefghijklmnopqrstuvwxyz" + "0123456789"
    choice = random.SystemRandom().choice
    return "_" + ''.join(choice(characters) for _ in range(identifierLength))

def is_matx_node(node):
    """Determines if the passed in node is a MaterialX Node."""
    return hasattr(node, "_is_matx_node")

def is_output_node(node):
    """Determines if the passed in node is an output node by looking for output sockets"""
    return not len(node.outputs)

def get_node_tree(node):
    """Gets the NodeTree(ID) Datablock from Blender that the passed in Node belongs to."""
    return node.id_data

def get_sockets(node):
    """Returns a joined list of input and output sockets for the passed in node"""
    return list(node.inputs) + list(node.outputs)

@node_parameter
def create_parameter(value, **kwargs):
    """Creates and registers a dynamic Blender Property property group using type()"""
    return value
# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#


class MaterialXNode(object):
    """Base MaterialX Node that all other nodes inherit from."""
    # Class Properties
    # Width, Max/Min
    bl_width_min = 40
    bl_width_max = 5000
    # MaterialX Node?
    _is_matx_node = True
    # Blender Properties
    identifier = StringProperty(name="Identifier", default="")
    active_input = IntProperty()
    active_output = IntProperty()
    _is_output_node = False

    '''Required functions for a Blender Node. Do not override in subclass'''

    @classmethod
    def poll(cls, ntree):
        """Determines if this node can be created in the current node tree."""
        return ntree.bl_idname == 'mx_MaterialXNodeTree'

    @classmethod
    def iter_node_bpy_types(cls):
        from nodeitems_utils import node_categories_iter
        from nodeitems_builtins import ShaderNewNodeCategory
        for cat in node_categories_iter(context=None):
            if '_NEW_' in cat.identifier:
                # for node_item in cat.items(context=None):
                yield from cat.items(context=None)

    def init(self, context):
        """Initialize a new instance of this node. Sets identifier to a random string."""
        self.identifier = create_identifier()
        self.setup()
        self.create()

    def update(self):
        """Update on editor changes. DO NOT USE"""
        pass

    def free(self):
        """Clean up node on removal"""
        self.delete()
        self._clear()

    def copy(self, source_node):
        """Initialize a new instance of this node from an existing node."""
        self.identifier = create_identifier()
        self.duplicate(source_node)

    def draw_buttons(self, context, layout):
        """Draws buttons on the node"""
        self.draw(layout)

    def draw_label(self):
        """Draws the node label. Should just return the bl_label set in subclass"""
        return self.bl_label

    '''Functions subclasses can override'''

    def duplicate(self, source_node):
        """Called when duplicating the node"""
        pass

    def edit(self):
        """Called when the node is edited"""
        pass

    def save(self):
        """Function to handle saving node properties when file is saved"""
        pass

    def create(self):
        """Function to create this node, called by init()"""
        pass

    def setup(self):
        """Function to setup this node, called by init(), before create()"""
        pass

    def remove(self):
        """Function to remove this node from it's node tree"""
        self.node_tree.nodes.remove(self)

    def delete(self):
        """Helper function for after this node has been deleted/removed"""
        pass

    def draw(self, layout):
        """Draw function"""
        pass

    '''Private functions. Here for convenience when subclassing'''

    def _new_input(self, type, name, identifier = None, **kwargs):
        """
        Create's a new input socket.
        :param type: socket data type
        :type type: any socket data type
        :param name: name of socket
        :type name: str
        :param identifier: identifier of the socket, used in code
        :type identifier: str
        :param kwargs: keyword arguments for special socket properties
        :return: socket
        """
        if identifier is None: identifier = name
        socket = self.inputs.new(type, name, identifier)
        self._set_socket_properties(socket, kwargs)
        return socket

    def _new_output(self, type, name, identifier = None, **kwargs):
        """
        Create's a new output socket.
        :param type: socket data type
        :type type: any socket data type
        :param name: name of socket
        :type name: str
        :param identifier: identifier of the socket, used in code
        :type identifier: str
        :param kwargs: keyword arguments for special socket properties
        :return: socket
        """
        if identifier is None: identifier = name
        socket = self.outputs.new(type, name, identifier)
        self._set_socket_properties(socket, kwargs)
        return socket


    def _clear(self):
        """Clears all data on this node."""
        self._clear_sockets()

    def _clear_sockets(self):
        """Clears all input and output sockets"""
        self._clear_inputs()
        self._clear_outputs()

    def _clear_inputs(self):
        """Clears all input sockets. Calls socket's free()
            and then removes all input sockets with inputs.clear()."""
        for socket in self.inputs:
            socket.free()
        self.inputs.clear()

    def _clear_outputs(self):
        """Clears all output sockets. Calls socket's free()
            and then removes all output sockets with outputs.clear()."""
        for socket in self.outputs:
            socket.free()
        self.outputs.clear()

    def _remove_socket(self, socket):
        """Removes any node socket by checking it's index and decrementing
         the value of the of the node's active input or output socket."""
        index = socket.get_index(self)
        if socket.is_output_socket:
            if index < self.active_output: self.active_output -= 1
        else:
            if index < self.active_input: self.active_input -= 1
        socket.sockets.remove(socket)

    def _set_socket_properties(self, socket, properties):
        """
        Function to set the properties of a node's sockets. 
        :param socket: bpy.types.NodeSocket()
        :param properties: dict
        :return: 
        """
        for key, value in properties.items():
            if key == 'link_limit':
                if hasattr(socket, '_is_list'):
                    setattr(socket, key, value)
            else:
                setattr(socket, key, value)


    '''Node Properties. Do not override unless absolutely necessary'''

    @property
    def node_tree(self):
        """Returrns the ID Datablock of this node's current NodeTree."""
        return self.id_data

    @property
    def inputs_by_id(self):
        """Returns all identifiers for this node's input sockets."""
        return {socket.identifier: socket for socket in self.inputs}

    @property
    def outputs_by_id(self):
        """Returns all identifiers for this node's output sockets."""
        return {socket.identifier: socket for socket in self.outputs}

    @property
    def sockets(self):
        """Returns a joined list of this node's input+output sockets."""
        return list(self.inputs) + list(self.outputs)

    @property
    def active_input_socket(self):
        """Returns the currently active input socket's index."""
        if len(self.inputs) == 0: return None
        return self.inputs[self.active_input]

    @property
    def active_output_socket(self):
        """Returns the currently active output socket's index."""
        if len(self.outputs) == 0: return None
        return self.outputs[self.active_output]


def set_materialx_node_type(self):
    for item in MaterialXNode.iter_node_bpy_types():
        # ''''''
        if ('Image' or 'Environment') in self.bl_idname:
            mtlx_type = 'image'
        elif 'Bsdf' in self.bl_idname:
            mtlx_type = repr(('shader', self.bl_idname))
        elif self.bl_idname == 'ShaderNodeAddShader' \
                or self.bl_idname == 'ShaderNodeMixShader':
            mtlx_type = repr(('shader', self.bl_idname))
        else:
            if len(self.outputs) > 0:
                mtlx_type = self.outputs[0].mtlx_type
            else:
                mtlx_type = 'shader'
        return mtlx_type
    else:
        if 'Renderman' in self.bl_idname:
            mtlx_type = 'shader'
        elif 'Pxr' in self.bl_idname:
            if len(self.outputs) > 0:
                mtlx_type = self.outputs[0].mtlx_type
            else:
                mtlx_type = self.outputs[0].mtlx_type
        return mtlx_type



def register():
    """Blender's register function. Injects methods and classes into Blender"""
    bpy.types.Node.is_matx_node = BoolProperty(name="MaterialX Node", get=is_matx_node)
    bpy.types.Node.is_output_node = BoolProperty(name="Output Node", get=is_output_node)
    bpy.types.Node.get_node_tree = get_node_tree
    bpy.types.Node.get_sockets = get_sockets
    bpy.types.Node.mtlx_type = StringProperty(get=set_materialx_node_type)

def unregister():
    """Blender's unregister function. Removes methods and classes from Blender"""
    del bpy.types.Node.is_matx_node
    del bpy.types.Node.is_output_node
    del bpy.types.Node.get_node_tree
    del bpy.types.Node.get_sockets
    del bpy.types.Node.mtlx_type