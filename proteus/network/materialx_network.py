# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    
:synopsis:
    Module defining a MaterialXNetwork class to hold a Node Tree system

:description:
    This module defines a MaterialXNetwork. This is a direct extension of a built in
    Material Node Tree inside of Blender, and functions as a way to collect and store
    important information about the Node Tree and it's contents.

:applications:
    Blender 3D
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
# MaterialX Imports
try:
    import MaterialX as mx
except ImportError:
    mx = None
    print("MaterialX Network Module could not load MaterialX library")
# Standard Imports
import os
# Standard Blender Imports
import bpy
from bpy.props import *
from bpy.app.handlers import persistent

from ...utils.io import IO

# Create the default MaterialX Library
uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
addon_path = uppath(__file__, 3)
mtlx_std_lib = os.path.join(addon_path, "lib", 'mtlx_lib', 'mx_stdlib_defs.mtlx')
mtlx_std_doc = mx.createDocument()
mx.readFromXmlFile(mtlx_std_doc, mtlx_std_lib)
IO.info("MaterialX Standard Library Loaded. Filepath: %s" % mtlx_std_lib)

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#
class MaterialXNetwork(object):
    """MaterialX Network class that holds t"""
    def __init__(self):
        """Initialization function for the MaterialXNetwork"""
        self.document = None
        self.material = None
        self.read_document = None # the read mtlx document from disk
        self.read_material = None # the blender mat a read document will be written to
        self.mtlx_mat = None
        self.node_graph = None
        self.output_node = None
        self.mtlx_output = None
        self.output_sockets = []
        self.ng_output_sockets = []
        self.mtlx_node_data = set()
        self._sockets = None
        self._socket_count = None
        self._render_engine = None

    '''-----------------------------------Network Methods------------------------------'''
    def setup(self):
        """Quick external data setup functions"""
        self.render_engine = bpy.context.scene.render.engine

    def init_network(self):
        """Initializes and returns a MaterialX Document()"""
        # Create and Initialize a Document
        if self.document is not None:
            self.document.initialize()
        else:
            self.document = mx.createDocument()
            self.document.initialize()
        # Run setup
        self.setup()
        # self.document.importLibrary(mtlx_std_doc.getDocument()) # import standard lib
        doc = self.document
        IO.info("MaterialX Version: %s|%s" % (doc.getVersionString(),
                                              mx.getVersionIntegers()))
        if self.material:
            IO.debug("Current Material: %s" % self.material.name)
            mtlx_mat = doc.addMaterial()
            mtlx_mat.setName(str(self.material.name))
            self.output_node = self.active_output
            IO.debug("Active Output Node: %s" % self.output_node.name)
            # Create a custom node def for the Cycles Material Output Node
            material_output = doc.addNodeDef(name='material_output_def',
                                             node='material_output',
                                             type='surfaceshader')
            # Add inputs to the Node definition
            surface = material_output.addInput(name='surface', type='surfaceshader')
            volume = material_output.addInput(name='volume', type='volumeshader')
            # Create custom TypeDef for displacement output
            disp = material_output.addInput(name='displacement', type='float')
            # Instance a Shader Ref. connect BindInputs to nodes
            mtlx_output = mtlx_mat.addShaderRef('mtlx_output', 'material_output')
            mtlx_output.setAttribute('xpos', str(self.output_node.location[0]))
            mtlx_output.setAttribute('ypos', str(self.output_node.location[1]))
            # Create Node Graph for this Material
            node_graph = doc.addNodeGraph("ng_%s" % self.material.name)
            node_graph.setNodeDef(material_output)
            ng_surface_out = node_graph.addOutput(name='ng_surface_out',
                                                  type='surfaceshader')
            ng_volume_out = node_graph.addOutput(name='ng_volume_out',
                                                 type='volumeshader')
            ng_disp_out = node_graph.addOutput(name='ng_disp_out', type='float')
            self.ng_output_sockets = [ng_surface_out, ng_volume_out, ng_disp_out]
            for link in self.yield_output_links():
                out_search = link[3] # look for the TO NODE socket in links
                # search for the right name
                out_name = ((str(out_search).split('.', 1)[0]).strip('()_.')).lower()
                # Set Nodename (creates connection) for the found socket)
                if out_name == 'surface': ng_surface_out.setNodeName(link[0])
                elif out_name == 'volume': ng_volume_out.setNodeName(link[0])
                elif out_name == 'displacement': ng_disp_out.setNodeName(link[0])
            self.node_graph = node_graph
            # BindInputs
            surface_bind = mtlx_output.addBindInput('surface', 'surfaceshader')
            volume_bind = mtlx_output.addBindInput('volume', 'volumeshader')
            disp_bind = mtlx_output.addBindInput('displacement', 'float')
            self.mtlx_mat = mtlx_mat #The Document's Material
            self.mtlx_output = mtlx_output # The instantiated material_output Node
            self.output_sockets = [surface_bind, volume_bind, disp_bind]
            self.connect_bind_input(surface_bind, self.node_graph, ng_surface_out)
            self.connect_bind_input(volume_bind, self.node_graph, ng_volume_out)
            self.connect_bind_input(disp_bind, self.node_graph, ng_disp_out)
            self.document = doc
            # Clear old Node Data first
            if self.mtlx_node_data:
                self.mtlx_node_data.clear()
            self.reset_mtlx_names()
            self.sockets = self.get_sockets()
            self.socket_count = self.get_socket_count()
            count = self.socket_count
            # self.set_unique_sockets(self.get_socket_count())
            IO.info("Setting Node Data")
            for node in self.yield_nodes(nodes=self.nodes):
                # Set Node's data: Current Material, and pass in current mtlx doc
                self.set_data(node, count)
        return doc

    def update_network(self):
        self.init_network()
        data_list = []
        for data in self.mtlx_node_data:
            if hasattr(data, 'instantiate'):
                data.instantiate(self.node_graph)
                data_list.append(data)
        IO.info("Connecting Nodes")
        for data in data_list:
            self.connect_nodes(data)
        self.write_network()

    def sort_network(self):
        doc = self.document
        materials = doc.getMaterials()
        graphs = doc.getNodeGraphs()

    def write_network(self):
        IO.debug("Writing mtlx to file")
        mx.writeToXmlFile(self.document, self.material.mtlx_props.doc_write)

    def read_network(self):
        if self.read_material is None:
            self.new_material()
        # Material Setup
        mat_output = self.reset_material()
        IO.debug("Reading MTLX from file")
        # Read document & get material ref
        self.read_document = mx.createDocument()
        mx.readFromXmlFile(self.read_document, self.material.mtlx_props.doc_read)
        mtlx_mat = self.read_document.getMaterial(self.material.name)
        IO.debug("MaterialX Material: %s" % mtlx_mat)
        # Get Shader Refs
        shader_refs = mtlx_mat.getShaderRefs()
        for shader_ref in shader_refs:
            IO.debug("Shader Ref: %s" % shader_ref)
            out_loc = [float(shader_ref.getAttribute('xpos')),
                       float(shader_ref.getAttribute('ypos'))]
            self.set_node_location(self.read_material, mat_output, out_loc)
            # Get inputs, outputs, and parameters
            inputs = shader_ref.getBindInputs() # unused, should point to outputs
            params = shader_ref.getBindParams() # for special properties
            outputs = shader_ref.getReferencedOutputs()
            for output in outputs:
                if output.getName() != "ng_surface_out":
                    continue
                # Graph Iterator:
                IO.info("Graph Traversal")
                # Get Edge Connection, i.e. NodeGraph
                for t_edge in output.traverseGraph(mtlx_mat):
                    IO.info("Traversing Graph")
                    # Get NodeGraph Output Socket
                    elem_down = t_edge.getDownstreamElement()
                    elem_up = t_edge.getUpstreamElement()
                    elem_connect = t_edge.getConnectingElement()
                    IO.debug("Downstream: %s" % elem_down)
                    IO.debug('Upstream: %s' % elem_up)
                    IO.debug("Connecting: %s" % elem_connect)
                    from .extension_defs import get_node_class_name
                    if elem_down.isA(mx.Output):
                        # Connect Downstream to Material Output
                        print("Output Element Found")
                        node_def = self.read_document.getMatchingNodeDefs(
                            elem_up.getName())[0]
                        node_idname = get_node_class_name(node_def.getName())
                        b_node = self.read_material.node_tree.nodes.new(node_idname)
                        b_node.location = [float(elem_up.getAttribute('xpos')),
                                           float(elem_up.getAttribute('ypos'))]
                        node_tree = self.read_material.node_tree
                        node_tree.links.new(
                            b_node.outputs[0], mat_output.inputs[0]
                        )
                        IO.debug('Node Class: %s' % node_idname)
                        node_inputs = node_def.getInputs()
                        for node_in in node_inputs:
                            self.set_socket_value(node_in, b_node)
                        node_params = node_def.getParameters()
                        for node_param in node_params:
                            self.set_param_value(node_param, b_node)
                    elif elem_down.isA(mx.Node):
                        # Connect Upstream Element, to Downstream Element, via Connect
                        node_name = elem_up.getName()
                        node_def = elem_up.getReferencedNodeDef()
                        node_def = self.read_document.getMatchingNodeDefs(
                            self.clean_name(node_name))[0]
                        # Get Blender Information
                        # grab the proper node class name
                        node_idname = get_node_class_name(node_def.getName())
                        # Create a new Blender Node
                        # Check existing nodes first
                        b_nodes = self.read_material.node_tree.nodes
                        b_node = b_nodes.get(self.from_mtlx_name(node_name), None)
                        if b_node is None:
                            b_node = self.read_material.node_tree.nodes.new(node_idname)
                        b_node.location = [float(elem_up.getAttribute('xpos')),
                                           float(elem_up.getAttribute('ypos'))]
                        node_tree = self.read_material.node_tree
                        # Get names from MTLX and normalize them
                        down_name = self.from_mtlx_name(elem_down.getName())
                        up_name = self.from_mtlx_name(elem_up.getName())
                        connect_name = self.normalize_name(elem_connect.getName())
                        if 'Bsdf' in up_name:
                            up_name = up_name.replace(up_name.split(" ")[1],
                                                      up_name.split(" ")[1].upper())
                        if 'Bsdf' in down_name:
                            down_name = down_name.replace(down_name.split(" ")[1],
                                                          down_name.split(" ")[1].upper())
                        down_node = node_tree.nodes[down_name]
                        up_node = node_tree.nodes[up_name]
                        down_port_idx = int(elem_down.getChildIndex(
                            elem_connect.getName()))
                        IO.debug("Connection Input Name: %s" % elem_connect.getName())
                        IO.debug("Connection Input Index: %s" % down_port_idx)
                        IO.debug("New Connection: %s, %s" % (
                            up_node.outputs[0].name,
                            down_node.inputs[down_port_idx].name))
                        node_tree.links.new(
                            up_node.outputs[0], down_node.inputs[down_port_idx]
                        )
                        IO.debug('Node Class: %s' % node_idname)
                        node_inputs = node_def.getInputs()
                        for node_in in node_inputs:
                            self.set_socket_value(node_in, b_node)
                        node_params = node_def.getParameters()
                        for node_param in node_params:
                            self.set_param_value(node_param, b_node)


    def new_material(self):
        """Create a new Blender Material"""
        new_material = bpy.data.materials.new("mtlx_%s" % self.material.name)
        new_material.use_nodes = True
        self.read_material = new_material
        return new_material

    def reset_material(self):
        """Reset the Material we're writing to."""
        self.read_material.node_tree.nodes.clear()
        output = self.read_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        return output

    '''----------------------------------Node Data Methods-----------------------------'''
    @property
    def socket_count(self):
        return self._socket_count
    @socket_count.setter
    def socket_count(self, value):
        self._socket_count = value

    def set_data(self, node, total_count):
        """Set a node's MTLX data, setup the node, and add it to the MaterialXNetwork()"""
        render_engine_classes = None
        # self.set_unique_socket_name(node)
        self.check_engine() # check to make sure our render engine was properly setup
        if self.render_engine == 'CYCLES':
            render_engine_classes = 'CYCLES'
        elif self.render_engine == 'PRMAN_RENDER':
            render_engine_classes = 'PRMAN'
        node.render_engine = render_engine_classes
        node_sockets = list(node.inputs) + list(node.outputs)
        for socket in node_sockets:
            # current_count = self.socket_count
            # IO.debug("Current Count: %d" % current_count)
            s_idx = self.increment_socket(self.socket_count)
            self.socket_count -= 1
            socket_name = "%s.%s" % (self.to_mtlx_name(socket.name), s_idx)
            socket.mtlx_name = socket_name
        data = node.mtlx_data()
        # Check to see if this node has a MTLX Implementation
        self.set_mtlx_data(data)

    def set_mtlx_data(self, data):
        if data is not None:
            IO.debug("Data Created")
            # Set the Custom Node's Material, doc, and pass this class to the node
            data.material = self.material
            data.doc = data.init_doc()
            data.mtlx_network = self
            data.setup()
            self.add_data(data)
            return data

    def add_data(self, data):
        """Add a node's MTLX data to the MaterialXNetwork()"""
        #TODO: Check if Node has already been added and clear the old node
        if data:
            self.mtlx_node_data.add(data)

    '''-------------------------------------Node Methods-------------------------------'''

    def yield_nodes(self, nodes):
        """Generator to get nodes from the passed in Material Nodes"""
        if nodes is None:
            nodes = self.nodes
        yield from [node for node in nodes]

    def update_nodes(self):
        """Update all nodes in """
        for node in self.yield_nodes(self.nodes):
            node.update()
            yield node

    def iter_update_nodes(self):
        """Iterate through all Blender Material Nodes and update them."""
        yield from (node for node in self.update_nodes())

    def connect_nodes(self, node_data):
        """Read a Node's Data and create the proper Node Links for that Node"""
        IO.info("Current Node: %s" % node_data.mtlx_name)
        # First get active output node and setup it's node links
        output_node = self.active_output
        for link in node_data.node_links:
            # # If the To Node for current node link is to material out
            # if link[2] == output_node.name: #connect node graph node to ng_out
            #     ng_out = self.node_graph.getOutput('')
            #     continue
            if link[2] == node_data.mtlx_name:
                # If this is the TO Node
                graph_node = node_data.mtlx_node_graph.getNode(link[0])
                IO.debug("From Node & Node Link")
                IO.debug("Node: %s" % graph_node)
                IO.debug("Link: %s:" % repr(link))
                IO.debug("To Node: %s" % node_data.mtlx_graph_node)
                IO.debug("Graph Node Inputs: %s" %
                         [i.getName() for i in node_data.mtlx_graph_node.getInputs()])
                # socket_name = (str(link[3]).replace(" ", "_")).lower()
                socket_name = str(link[3])
                IO.debug("Current Socket Name: %s " % socket_name)
                socket = node_data.mtlx_graph_node.getInput(socket_name)
                IO.debug("Socket: %s" % socket)
                socket.setConnectedNode(graph_node)

    def iter_node_links(self):
        """Iterate through all node links for this Material"""
        return {node_link for node_link in self.yield_node_links(self.node_links)}

    def yield_node_links(self, links):
        """Yield node links for the blender Material"""
        if links is not None:
            yield from self.build_links(links)
        else:
            yield from self.build_links(self.node_links)

    def build_links(self, links):
        """
        Build Node Links for the MaterialX Network
        Args:
            links:
                Blender Material Node Links
        Returns:
            link_tuple(from_node, from_socket, to_node, to_socket)
        """
        for link in links:
            if link.is_valid:
                link_tuple = (self.to_mtlx_name(link.from_node.name),
                              link.from_socket.mtlx_name,
                              self.to_mtlx_name(link.to_node.name),
                              link.to_socket.mtlx_name)
                yield link_tuple
            else:
                continue

    def get_active_output(self):
        """Get the active Material Output Node"""
        for node in self.yield_nodes(nodes=None):
            if node.is_output_node is True:
                if hasattr(node, 'is_active_output'):
                    if node.is_active_output is True:
                        return node
                else:
                    return node

    def yield_output_links(self):
        """Generator to get all links for the Material Output Node"""
        yield from [link for link in self.iter_node_links()
                    if link[2] == self.to_mtlx_name(self.active_output.name)]

    '''------------------------------Socket/Connection Methods-------------------------'''

    def init_node_graph(self):
        """Initialize the Blender Material's MTLX Node Graph network"""
        pass

    def connect_bind_input(self, bind_input, node_graph, ng_out):
        """Connect a MTLX BindInput() to a MTLX NodeGraph() output socket"""
        bind_input.setNodeGraphString(node_graph.getName())
        bind_input.setConnectedOutput(ng_out)

    def get_sockets(self):
        sockets = []
        for node in self.nodes:
            # Loop through sockets, append socket.mtlx_name to lists
            for socket_name in self.yield_socket_names(node, 'inputs'):
                sockets.append((node, socket_name, 'input'))
            for socket_name in self.yield_socket_names(node, 'outputs'):
                sockets.append((node, socket_name, 'output'))
        return sockets

    def yield_socket_names(self, node, type):
        # IO.debug("Yielding Sockets")
        if type == 'inputs':
            if len(node.inputs) > 0:
                yield from [i.name for i in node.inputs]
        elif type == 'outputs':
            if len(node.outputs) > 0:
                yield from [o.name for o in node.outputs]

    def yield_sockets(self):
        sockets = [([i for i in list(node.inputs)]) + ([o for o in list(node.outputs)])
                   for node in self.nodes]
        yield sockets

    def reset_mtlx_names(self):
        IO.info("Resetting MTLX Names")
        for node in self.nodes:
            for input in node.inputs:
                input.mtlx_name = ""
            for output in node.outputs:
                output.mtlx_name = ""

    def increment_socket(self, count):
        idx = ""
        if count == 0:
            idx = '000'
        elif count < 10:
            idx = str('{}{}').format('00', str(count))
        elif count < 100:
            idx = str('{}{}').format('0', str(count))
        elif count > 100:
            idx = str(count)
        if count == 0:
            idx = str(count)
        return idx

    def get_socket_count(self):
        count = 0
        for node in self.nodes:
            if len(node.inputs) > 0:
                for i_socket in node.inputs:
                    count += 1
            if len(node.outputs) > 0:
                for o_socket in node.outputs:
                    count += 1
        IO.debug("Socket Count: %d" % count)
        return count

    def set_socket_value(self, node_in, b_node):
        """
        Set the socket value of a Blender node based on th MTLX Input() information
        Args:
            node_in: MTLX Node Input()
            b_node: Blender Node

        Returns:
            None
        """
        # Pull info from the MaterialX Input()
        in_value = node_in.getValue()
        in_type = node_in.getType()
        in_name = self.normalize_name(node_in.getName())
        # in_name = (str(node_in.getName()).replace("_", " ")).title()
        # Set Socket Value
        if in_name =='Ior':
            in_name = 'IOR'
        if in_type == 'float':
            try:
                b_node.inputs[in_name].default_value = float(in_value)
            except KeyError:
                print("Blender Node Input not found")
                # b_node.inputs[(in_name.upper())].default_value = float(in_value)
        elif "vector" in in_type or "color" in in_type:
            value = [float(x) for x in str(in_value).split(',')]
            for i, v in enumerate(value):
                try:
                    b_node.inputs[in_name].default_value[i] = v
                except KeyError:
                    print("Blender Node Input not found")
                    # b_node.inputs[(in_name.upper())].default_value[i] = v

    def set_param_value(self, node_param, b_node):
        """
        Set the param value of a Blender node based on th MTLX Input() information
        Args:
            node_param: MTLX Parameter()
            b_node: Blender Node

        Returns:
            None
        """
        # Check if the Node has the passed in node_param attribute
        if hasattr(b_node, node_param.getName()):
            param_type = node_param.getType()
            # Set the Blender Node parameter
            if param_type == 'string':
                try:
                    setattr(b_node, node_param.getName(), node_param.getValue())
                except TypeError:
                    IO.error("Cannot set the Node's attribute. \n "
                          "Node: %s.%s; Continuing..." %
                          (b_node.name, node_param.getName()))
                    pass
            elif 'float' in param_type:
                setattr(b_node, node_param.getName(),
                        float(node_param.getValue()))
            elif 'vector' in param_type:
                setattr(b_node, node_param.getName(),
                        [float(x) for x in node_param.getValue()])
            elif 'color' in param_type:
                setattr(b_node, node_param.getName(),
                        [float(x) for x in node_param.getValue()])
            elif param_type == 'filename':
                IO.warning("Need to load external file: %s" %
                           os.path.basename(node_param.getValue()))
                image = bpy.data.images.load(node_param.getValue(), check_existing=True)
                b_node.image = image
        else:
            IO.warning("Parameter {} not found for node {}".format(
                node_param.getName(), b_node.name))
    '''-----------------------------------Class Methods--------------------------------'''

    @staticmethod
    def join_document(cls, matx_doc):
        """Joins the passed matx_doc with an initialized document"""
        # Initialize the network, pass the class doc by reference to a temp_doc variable
        temp_doc = cls.document
        # Grab a pointer reference to the Document() element of a MaterialX document
        doc_ptr = matx_doc.getDocument()
        # Copy the doc_ptr's content to the temp_doc
        temp_doc.copyContentFrom(doc_ptr)
        # Create a joined document and return it from this function
        join_doc = temp_doc
        return join_doc

    @classmethod
    def increment_name(cls, name):
        if "." in name:
            name_index, name_string = int(str(name).split(".", 1)[1]), \
                                      str(name).split(".", 1)[0]
        else:
            name_index = 0
            name_string = name
        name_index += 1
        idx = ""
        if name_index < 10:
            idx = str('{}{}').format('00', str(name_index))
        elif name_index < 100:
            idx = str('{}{}').format('0', str(name_index))
        elif name_index > 100:
            idx = str(name_index)
        new_name = "%s.%s" % (name_string, idx)
        return new_name

    @classmethod
    def to_mtlx_name(cls, name):
        """Create's a correct MTLX name"""
        return (str(name).lower()).replace(" ", "_")

    @classmethod
    def from_mtlx_name(cls, name):
        """Deserialie a proper MTLX name"""
        return (str(name).replace("_", " ")).title()

    @classmethod
    def normalize_name(cls, name):
        name = name.split(".", 1)[0]
        new_name = " ".join([n.capitalize() for n in name.split("_")])
        return new_name

    @classmethod
    def clean_name(cls, name):
        name = name.split(".", 1)[0]
        return name


    @classmethod
    def set_node_location(cls, material, node, loc):
        material.node_tree.nodes[node.name].location = loc

    '''-----------------------------------Property API---------------------------------'''

    @property
    def node_tree(self):
        """The Blender Material ShaderNodeTree"""
        return self.material.node_tree

    @property
    def nodes(self):
        """Nodes in the Blender Material's ShaderNodeTree"""
        return self.node_tree.nodes

    @property
    def node_link_set(self):
        """A set() of Node Links for this Blender Material's Node Network"""
        return self.iter_node_links()

    @property
    def node_links(self):
        """All of the Blender Material ShaderNodeTree's Node Links"""
        return self.node_tree.links

    @property
    def active_output(self):
        """The active Material Output Node for this Blender Material"""
        return self.get_active_output()

    @property
    def render_engine(self):
        """The Current Render Engine"""
        return self._render_engine
    @render_engine.setter
    def render_engine(self, engine):
        if self._render_engine != bpy.context.scene.render.engine:
            self._render_engine = engine
    def check_engine(self):
        if self.render_engine is None:
            self.render_engine = bpy.context.scene.render.engine

    @property
    def sockets(self):
        return self._sockets
    @sockets.setter
    def sockets(self, value):
        self._sockets = value



class StringResolver(object):
    @classmethod
    def normalize_camel_case(cls, name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def register():
    """Blender's register function. Injects methods and classes into Blender"""
    bpy.types.Material.mtlx_network = MaterialXNetwork()


def unregister():
    """Blender's unregister function. Removes methods and classes from Blender"""
    del bpy.types.Material.mtlx_network