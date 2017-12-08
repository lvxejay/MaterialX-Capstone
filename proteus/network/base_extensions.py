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

# MaterialX Import. Run in a try statement to ensure MaterialX is installed in the appli-
# cation's python directory.
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

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#


# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

'''Base Classes: All Custom MTLX Nodes Inherit from here'''


class MtlxCustomNode(object):
    """
    Base MTLX Node Class
    """

    def __init__(self, node):
        # The MaterialXNetwork Document, always public
        self.doc = None
        self.instantiated = False
        self.defined = False
        # Blender Variables
        self.node = node  # the blender node
        self.params = None  # node parameters
        self.material = None  # the material this node belongs to
        self.location = tuple(node.location)  # location of the node in the node_tree
        self.inputs = node.inputs  # node input sockets
        self.outputs = node.outputs  # node output sockets
        self.links = []  # links to or from this node
        # Private Vars, accessible via Property API
        self._mtlx_mat = None  # The MTLX Material()
        self._mtlx_node_def = None  # the nodedef()
        self._mtlx_node_def_name = None  # the node_def's name
        self._mtlx_node = None  # the mtlx_node
        self._mtlx_inputs = []
        self._mtlx_outputs = []
        self._mtlx_params = []
        self._mtlx_shader_refs = []
        self._mtlx_type = None
        self._mtlx_node_graph = None
        self._mtlx_graph_node = None
        self._mtlx_network = None
        self._mtlx_target = None

    '''-----------------------------------METHODS--------------------------------------'''

    def setup(self):
        """
        Setup function for this node. Called after the node has been initialized in the
        MaterialXNetwork() and after it has been passed the proper initial arguments to
        successfully complete setup.
        Returns:
            None
        """
        # Set MTLX Inputs, Outputs, & Params in the pattern (name, type, value)
        self.mtlx_inputs = self.get_inputs()
        self.mtlx_outputs = self.get_outputs()
        self.mtlx_params = self.get_params()
        self.set_mtlx_type()
        self.mtlx_node_def_name = self.idname
        self.create_node_def()
        # get NodeDefs, ShaderRefs, and Material
        self.mtlx_node_def = self.doc.getNodeDef(self.mtlx_node_def_name)
        self.mtlx_shader_refs = self.mtlx_node_def.getInstantiatingShaderRefs()
        self.mtlx_mat = self.doc.getMaterial(self.material.name)

    def create_node_def(self, **kwargs):
        """
        Instantiates the python node into the MaterialX Document
        Args:
            **kwargs:
                *unused for now
        Returns:
            None
        """
        # Check to see if this NodeDef has already been defined
        if self.defined is True:
            return
        # Reference MTLX Information
        outputs = self.mtlx_outputs
        inputs = self.mtlx_inputs
        parameters = self.mtlx_params
        node_def_name = self.mtlx_node_def_name
        node_type = self.mtlx_type
        if self.doc.getNodeDef(self.mtlx_node_def_name) is not None:
            self.defined = True
            return

        # Add the Node Def to the Current MTLX Document
        node_def = self.doc.addNodeDef(name=node_def_name,
                                       node=self.mtlx_node,
                                       type=node_type)
        # Set CYCLES Node target
        node_def.setTarget(self.mtlx_target)
        # Create, Inputs, Outputs, and Parameters
        self.create_mtlx_inputs(node_def, inputs)
        self.create_mtlx_outputs(node_def, outputs)
        self.create_mtlx_parameters(node_def, parameters)
        # Set flag to true to avoid duplicate NodeDef creation
        self.defined = True

    def pre_instantiate(self, node_graph):
        """Handle any remaining node setup before instantiation in a MTLX NodeGraph()"""
        IO.info("Instantiating Node: %s" % self.mtlx_name)
        # Set the MTLX Node Graph from a MTLX Material's passed in NodeGraph()
        self.mtlx_node_graph = node_graph
        if self.instantiated is True:
            # Remove the Node if it has already been instantiated once to prevent duplis
            IO.debug("Removing Node, Already Instantiated")
            self.mtlx_node_graph.removeNode(self.mtlx_name)
        # Create and Add a Graph Node
        self.mtlx_graph_node = self.add_graph_node(
            node=self.mtlx_node, name=self.mtlx_name, type=self.mtlx_type)
        # Set this node's location in the node_graph
        self.mtlx_graph_node.setAttribute('xpos', str(self.location[0]))
        self.mtlx_graph_node.setAttribute('ypos', str(self.location[1]))

        # Set Graph Node Inputs and Parameters
        self.set_graph_node_inputs(self.mtlx_inputs)
        self.set_graph_node_parameters(self.mtlx_params)

        # Set flag to prevent duplicate instantiations
        self.instantiated = True

    def instantiate(self, node_graph):
        """Instantiate the Custom Node into the MTLX Node Graph"""
        self.pre_instantiate(node_graph)

    def add_graph_node(self, **kwargs):
        """

        Args:
            **kwargs:
            node: The name of the Node Def/Category
            name: The name of the node in the node_graph
            typeString: The type this node outputs

        Returns:
            mtlx_graph_node
        """
        mtlx_graph_node = self.mtlx_node_graph.addNode(
            kwargs.get('node'),
            name=kwargs.get('name'),
            typeString=kwargs.get('type')
        )
        return mtlx_graph_node

    def init_doc(self):
        """Initializes the MTLX Document from the MTLX Material or creates a new one"""
        if self.material:
            doc = self.material.mtlx_network.document
        else:
            IO.debug("Creating New Doc")
            doc = mx.createDocument()
            doc.initialize()
        # TODO: Standard MaterialX Library Import
        #  doc.importLibrary(mtlx_std_doc.getDocument())
        self.doc = doc
        return doc

    def clear_doc(self):
        """Reinitializes the Node's MTLX Doc, clearing the current doc content"""
        return self.doc.initialize()

    def iter_params(self):
        """Iterate through the parameters of this node"""
        if self.params:
            yield from [self.get_node_param(self.node, param) for param in self.params]
        else:
            yield

    def get_node_param(self, node, param):
        """Gets a node parameter and returns a tuple of its name, type and value"""
        if hasattr(node, param):
            # Return (name, type, value)
            param_value = (getattr(node, param))  # get param value
            param_type = str(node.bl_rna.properties[str(param)].type)  # get blender type
            param_name = MaterialXNetwork.to_mtlx_name(param)  # mtlx name
            if param_type in ['POINTER', 'ENUM']:  # check param type
                param_type = 'string'
            # check to see if we have a vector
            if isinstance(param_value, mathutils.Vector):
                param_value = param_value.to_tuple()
                str(param_value).strip("()")
            # check for Euler
            elif isinstance(param_value, mathutils.Euler):
                param_value = param_value[:]
            # check for boolean
            elif param_type == 'BOOLEAN':
                param_type = 'boolean'
            # get rid of extra chars and transform to string for mtlx
            param_value = str(param_value).strip("()")
            return (param_name, param_type, param_value)

            # else: return list

    @staticmethod
    def get_socket_value(node, socket):
        """Returns a tuple of a node socket's name, type, and value"""
        # Return a properly cased name
        socket_name = MaterialXNetwork.to_mtlx_name(socket.name)
        mtlx_type = socket.mtlx_type
        mtlx_name = socket.mtlx_name
        if socket.mtlx_type == 'shader':
            value = None
        else:
            value = socket.default_value
        if value is not None:
            if hasattr(value, "__len__"):
                ret = str(', '.join(repr(e) for e in value[:]))
                # socket_key = MaterialXNetwork.to_mtlx_name(socket_key)
                return (socket_name, mtlx_type, ret, mtlx_name)
            else:
                # socket_key = MaterialXNetwork.to_mtlx_name(socket_key)
                return (socket_name, mtlx_type, str(value), mtlx_name)
        else:
            return (socket_name, mtlx_type, value, mtlx_name)

    @staticmethod
    def get_socket_value_from_keys(node, socket_key, output):
        """Returns a tuple of a node socket's name, type, and value"""
        # Return a properly cased name
        socket_name = MaterialXNetwork.to_mtlx_name(socket_key)
        mtlx_name = ''
        if output is True:
            mtlx_type = node.outputs[socket_key].mtlx_type
            mtlx_name = node.outputs[socket_key].mtlx_name
            if node.outputs[socket_key].mtlx_type == 'shader':
                value = None
            else:
                value = node.outputs[socket_key].default_value
        else:
            mtlx_type = node.inputs[socket_key].mtlx_type
            mtlx_name = node.inputs[socket_key].mtlx_name
            if node.inputs[socket_key].mtlx_type == 'shader':
                value = None
            else:
                value = node.inputs[socket_key].default_value
        if value is not None:
            if hasattr(value, "__len__"):
                ret = str(', '.join(repr(e) for e in value[:]))
                # socket_key = MaterialXNetwork.to_mtlx_name(socket_key)
                return (socket_name, mtlx_type, ret, mtlx_name)
            else:
                # socket_key = MaterialXNetwork.to_mtlx_name(socket_key)
                return (socket_name, mtlx_type, str(value), mtlx_name)
        else:
            return (socket_name, mtlx_type, value, mtlx_name)

    def get_inputs(self):
        return [self.get_socket_value(self.node, i)
                for i in self.node.inputs]

    def get_outputs(self):
        return [self.get_socket_value(
            self.node, o) for o in self.node.outputs]

    def get_params(self):
        return [p for p in self.iter_params() if p is not None]

    def set_mtlx_type(self):
        # Literal Eval to read the internal node.mtlx_type property from Blender
        from ast import literal_eval
        if self.node.mtlx_type != 'image':
            if 'vector' in self.node.mtlx_type \
                    or 'color' in self.node.mtlx_type \
                    or 'float' in self.node.mtlx_type:
                self.mtlx_type = self.node.mtlx_type
            else:
                self.mtlx_type = literal_eval(self.node.mtlx_type)[0]
        else:
            self.mtlx_type = self.node.mtlx_type

    def create_mtlx_inputs(self, mtlx_node, inputs):
        if len(inputs) >= 1:
            in_type = inputs[0][1]
            for input in inputs:
                in_name, in_value, in_mtlx_name = input[0], input[2], input[3]
                if in_value is not None:
                    mtlx_input = mtlx_node.addInput(name=in_mtlx_name, type=input[1])
                    try:
                        mtlx_input.setValue(in_value, input[1])
                    except IndexError:
                        continue
                else:
                    try:
                        mtlx_input = mtlx_node.addInput(name=in_mtlx_name, type=input[1])
                    except LookupError:
                        print("NON UNIQUE NAME ERROR")
        # Output ONLY Node with no input sockets. Do nothing.
        elif len(inputs) == 0:
            pass

    def create_mtlx_outputs(self, mtlx_node, outputs):
        # Multioutput Node
        if len(outputs) > 1:
            out_type = 'multioutput'
            mtlx_node.setType(out_type)
            for output in outputs:
                mtlx_node.addOutput(name=output[3], type=output[1])

        # Single Output node output sockets are pre-defined by it's MTLX type
        elif len(outputs) == 1:
            for output in outputs:
                mtlx_node.addOutput(name=output[3], type=output[1])

    def create_mtlx_parameters(self, mtlx_node, parameters):
        # Setup node parameters
        if parameters is not None:
            if len(parameters) >= 1:
                for parameter in parameters:
                    mtlx_node.addParameter(name=parameter[0], type=parameter[1])
                    mtlx_node.setParameterValue(parameter[0], parameter[2], parameter[1])

    def set_graph_node_inputs(self, inputs):
        if len(inputs) >= 1:
            in_type = inputs[0][1]
            for input in inputs:
                try:
                    new_input = self.mtlx_graph_node.addInput(name=input[3],
                                                              type=input[1])
                    new_input.setInterfaceName(input[3])
                except LookupError:
                    print("NON UNIQUE NAME ERROR")

    def set_graph_node_parameters(self, parameters):
        if (parameters is not None) and (len(parameters) >= 1):
            for parameter in parameters:
                self.mtlx_graph_node.addParameter(name=parameter[0], type=parameter[1])
                self.mtlx_graph_node.setParameterValue(parameter[0],
                                                       parameter[2],
                                                       parameter[1])

    def reset(self):
        """Reset this node to it's default state."""
        # TODO: Implement Reset
        pass

    '''--------------------------Node Property API-------------------------------------'''

    # Blender Properties -----------------------------------------------------------------

    @property
    def idname(self):
        """The bl_idname of the Blender Node"""
        return str(self.node.bl_idname).lower()

    @property
    def node_tree(self):
        """Returns the ID Datablock of this node's current NodeTree."""
        return self.node.id_data

    @property
    def node_links(self):
        """Node Links for this Node"""
        return [x for x in self.mtlx_network.yield_node_links(self.node_tree.links)
                if self.mtlx_name == MaterialXNetwork.to_mtlx_name(x[0]) or
                self.mtlx_name == MaterialXNetwork.to_mtlx_name(x[2])]

    # MTLX Properties --------------------------------------------------------------------

    @property
    def mtlx_network(self):
        """The MaterialX Network """
        return self._mtlx_network

    @mtlx_network.setter
    def mtlx_network(self, cls):
        self._mtlx_network = cls

    @property
    def mtlx_name(self):
        """The proper MaterialX name for this Node"""
        return str((self.node.name).lower()).replace(" ", "_")

    @property
    def mtlx_mat(self):
        """The MaterialX Material this node is from."""
        return self._mtlx_mat

    @mtlx_mat.setter
    def mtlx_mat(self, value):
        self._mtlx_mat = value

    @property
    def mtlx_node_def(self):
        """The MTLX Custom Node Definition for this Node"""
        return self._mtlx_node_def

    @mtlx_node_def.setter
    def mtlx_node_def(self, value):
        self._mtlx_node_def = value

    @property
    def mtlx_node_def_name(self):
        """The Name Attribute of the MTLX Custon Node Definition for this Node"""
        return self._mtlx_node_def_name

    @mtlx_node_def_name.setter
    def mtlx_node_def_name(self, value):
        self._mtlx_node_def_name = value

    @property
    def mtlx_node(self):
        """The name of the node that implements this MTLX NodeDef"""
        return self._mtlx_node

    @mtlx_node.setter
    def mtlx_node(self, value):
        self._mtlx_node = value

    @property
    def mtlx_inputs(self):
        """List of input sockets in the patter [(name, type, default_value)]"""
        return self._mtlx_inputs

    @mtlx_inputs.setter
    def mtlx_inputs(self, value):
        self._mtlx_inputs = value

    @property
    def mtlx_outputs(self):
        """List of output sockets in the pattern [(name, type, default_value)]"""
        return self._mtlx_outputs

    @mtlx_outputs.setter
    def mtlx_outputs(self, value):
        self._mtlx_outputs = value

    @property
    def mtlx_params(self):
        """List of node parameters in the pattern [(name, type, default_value)]"""
        return self._mtlx_params

    @mtlx_params.setter
    def mtlx_params(self, value):
        self._mtlx_params = value

    @property
    def mtlx_shader_refs(self):
        """All Shader References that implement this Node Definition within a MTLX Doc"""
        return self._mtlx_shader_refs

    @mtlx_shader_refs.setter
    def mtlx_shader_refs(self, value):
        self._mtlx_shader_refs = value

    @property
    def mtlx_node_graph(self):
        """The MaterialX Node Graph this Node belongs to."""
        return self._mtlx_node_graph

    @mtlx_node_graph.setter
    def mtlx_node_graph(self, value):
        self._mtlx_node_graph = value

    @property
    def mtlx_graph_node(self):
        """The instantiated MaterialX Node within a NodeGraph()"""
        return self._mtlx_graph_node

    @mtlx_graph_node.setter
    def mtlx_graph_node(self, value):
        self._mtlx_graph_node = value

    @property
    def mtlx_type(self):
        """The MaterialX 'type' this Node outputs."""
        return self._mtlx_type

    @mtlx_type.setter
    def mtlx_type(self, value):
        self._mtlx_type = str(value)

    @property
    def mtlx_target(self):
        return self._mtlx_target
    @mtlx_target.setter
    def mtlx_target(self, target_name):
        self._mtlx_target = str(target_name)