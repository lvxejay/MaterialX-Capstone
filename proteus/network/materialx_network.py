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
def get_mtlx_net(material):
    """Generate a MaterialXNetwork() class"""
    network = MaterialXNetwork(material)
    return network
# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#
class MaterialXNetwork(object):
    """
    MaterialX Network is a representative, pythonic object based on a Blender Material
    This network tracks important data including: current material, node_tree, nodes,
    node sockets, links between node sockets, positions of the nodes, and any connections
    between the nodes.
    
    An exposed property API query's Blender for the data
    
    Class methods are shared between classes, which doesn't require an instance of this
    object to work, meaning the methods will work out of context and in broader scope.
    
    Static methods only operate on out of scope data that is pertinent to the behavior of
    the Network
    
    Instance methods provide the main functionalities of a MaterialXNetwork, primarily
    reading, writing, and encoding data into the MaterialX Specification format.
    
    """
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
        """Synchronize any external data and store it in the class instance"""
        self.render_engine = bpy.context.scene.render.engine

    def init_network(self):
        """Initializes and returns a MaterialX Document() for a Blender Material"""
        # Create and Initialize a Document
        IO.info("Initiating Network")
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
        # Every material should have a network
        if self.material:
            IO.debug("Current Material: %s" % self.material.name)
            # Add a material to do document
            mtlx_mat = doc.addMaterial()
            mtlx_mat.setName(str(self.material.name))
            # Grab the currently active output node and store it
            self.output_node = self.active_output
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

            # Iterate over each output link
            for link in self.yield_output_links():
                out_search = link[3] # look for the TO NODE socket in links
                # search for the right name
                out_name = ((str(out_search).split('.', 1)[0]).strip('()_.')).lower()
                # Set Nodename (which creates a connection in MTLX) for the found socket
                if out_name == 'surface': ng_surface_out.setNodeName(link[0])
                elif out_name == 'volume': ng_volume_out.setNodeName(link[0])
                elif out_name == 'displacement': ng_disp_out.setNodeName(link[0])
            self.node_graph = node_graph

            # Add and Connect BindInputs for the MTLX ShaderRef
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

            # Clear any old node data
            if self.mtlx_node_data:
                self.mtlx_node_data.clear()
            self.reset_mtlx_names()
            self.sockets = self.get_sockets()
            self.socket_count = self.get_socket_count()
            count = self.socket_count

            # Set Node's data: Current Material, and pass in current mtlx doc
            IO.info("Setting Node Data")
            for node in self.yield_nodes(nodes=self.nodes):
                self.set_data(node, count)

        # Return the encoded document
        return doc


    def update_network(self):
        """Update the MaterialXNetwork by re-running its initilization"""
        self.init_network()
        IO.info("Updating Network")
        # Instantiate each node into the Node Graph
        IO.debug("Instantiating Nodes")
        data_list = []
        for data in self.mtlx_node_data:
            if hasattr(data, 'instantiate'):
                data.instantiate(self.node_graph)
                data_list.append(data)

        # Connect each node
        IO.debug("Connecting Nodes")
        for data in data_list:
            self.connect_nodes(data)

        # Write the MaterialXNetwork to disk
        self.write_network()


    def sort_network(self):
        """Topologically Sort the MaterialXNetwork"""
        # doc = self.document
        # materials = doc.getMaterials()
        # graphs = doc.getNodeGraphs()
        """Not yet implemented as of MaterialX Version 1.35.4"""
        pass


    def write_network(self):
        """Write the MaterialXNework to a specified path on disk"""
        IO.info("Writing Network to MaterialX")
        mx.writeToXmlFile(self.document, self.material.mtlx_props.doc_write)


    def read_network(self):
        """
        Read and Create a MaterialX Network from a .mtlx file on disk
        Creates a new Blender Material with the same node graph as from it's source
        :return: 
        """
        if self.read_material is None:
            self.new_material()

        # Material Setup
        mat_output = self.reset_material()
        IO.debug("Reading MTLX from file")
        # Read document & get material ref
        self.read_document = mx.createDocument()
        mx.readFromXmlFile(self.read_document, self.material.mtlx_props.doc_read)
        mtlx_mat = self.read_document.getMaterial(self.material.name)
        IO.debug("--- MTLX Material: %s ---" % mtlx_mat)
        # Get Shader Refs
        shader_refs = mtlx_mat.getShaderRefs()
        for shader_ref in shader_refs:
            IO.debug("Shader Ref: %s" % shader_ref)
            out_loc = [float(shader_ref.getAttribute('xpos')),
                       float(shader_ref.getAttribute('ypos'))]
            self.set_node_location(self.read_material, mat_output, out_loc)

            # Get inputs, outputs, and parameters
            inputs = shader_ref.getBindInputs()  # unused, should point to outputs
            params = shader_ref.getBindParams()  # for special properties
            outputs = shader_ref.getReferencedOutputs()

            # Get the Surface Output
            #TODO: Implement Support for Volume and Displacement semantics
            for output in outputs:
                if output.getName() != "ng_surface_out":
                    continue

                # Get Edge Connection, i.e. NodeGraph
                connected_node = output.getConnectedNode()
                if connected_node is None:
                    continue

                b_node = self.get_bnode(connected_node)
                b_node_id = b_node.bl_idname
                IO.debug(connected_node)
                #TODO: node.getReferencedNodeDef() is deprecated
                node_def = self.get_node_def(self.read_document, b_node_id)
                node_inputs = node_def.getInputs()
                node_params = node_def.getParameters()
                self.set_bnode_inputs(node_inputs, b_node)
                self.set_bnode_params(node_params, b_node)
                self.read_material.node_tree.links.new(
                    b_node.outputs[0], mat_output.inputs[0]
                )
                # Graph Iterator:
                IO.info("Traversing Dataflow Graph")
                for t_edge in connected_node.traverseGraph(mtlx_mat):
                    IO.info("--- Edge ---")

                    # Get Edge Elements
                    elem_down = t_edge.getDownstreamElement()
                    elem_up = t_edge.getUpstreamElement()
                    elem_connect = t_edge.getConnectingElement()

                    # Print Element Names
                    IO.debug('Upstream: %s' % elem_up)
                    IO.debug("Downstream: %s" % elem_down)
                    IO.debug("Connecting: %s" % elem_connect)

                    # Get Upstream Node And Downstream Node names
                    down_name = self.normalize_node_name(
                        self.from_mtlx_name(elem_down.getName())
                    )
                    up_name = self.normalize_node_name(
                        self.from_mtlx_name(elem_up.getName())
                    )
                    connect_name = self.normalize_name(elem_connect.getName())

                    # Print Element Names
                    IO.debug("--- Normalized Element Names ---")
                    IO.debug(down_name)
                    IO.debug(up_name)
                    IO.debug(connect_name)

                    # Find or create new nodes
                    down_node = self.get_bnode(elem_down)
                    up_node = self.get_bnode(elem_up)
                    down_port_idx = int(elem_down.getChildIndex(
                        elem_connect.getName()))

                    # Print Connection Data
                    IO.debug("--- Blender Nodes and Connection ---")
                    IO.debug("New Connection: \n "
                             "Upstream Node <%s> & Socket <%s> | TO | "
                             "Downstream Node <%s> & Socket <%s> " %
                             (
                                 up_node.name,
                                 up_node.outputs[0].name,
                                 down_node.name,
                                 down_node.inputs[down_port_idx].name)
                             )
                    IO.debug("--- Connection Data ---")
                    IO.debug("Connection Input Name: %s" % elem_connect.getName())
                    IO.debug("Connection Input Index: %s" % down_port_idx)

                    # Link Upstream Node TO Downstream Node
                    self.read_material.node_tree.links.new(
                        up_node.outputs[0],
                        down_node.inputs[down_port_idx]
                    )
                    self.iter_upstream(elem_connect, mtlx_mat)

        IO.info("MaterialX Document Imported")

    def iter_upstream(self, elem, mtlx_mat):
        """
        
        :param elem: Connecting Element (Input) 
        :param mtlx_mat: 
        :return: 
        """
        connected_node = elem.getConnectedNode()
        if connected_node is None:
            return
        b_node = self.get_bnode(connected_node)
        b_node_id = b_node.bl_idname
        IO.debug(connected_node)
        # TODO: node.getReferencedNodeDef() is deprecated
        node_def = self.get_node_def(self.read_document, b_node_id)
        node_inputs = node_def.getInputs()
        node_params = node_def.getParameters()
        self.set_bnode_inputs(node_inputs, b_node)
        self.set_bnode_params(node_params, b_node)
        for t_edge in elem.traverseGraph(mtlx_mat):
            IO.info("--- Edge ---")
            # Get Edge Elements
            elem_down = t_edge.getDownstreamElement()
            elem_up = t_edge.getUpstreamElement()
            elem_connect = t_edge.getConnectingElement()
            # Print Element Data
            IO.debug('Upstream: %s' % elem_up)
            IO.debug("Downstream: %s" % elem_down)
            IO.debug("Connecting: %s" % elem_connect)
            # Get Upstream Node And Downstream Node names
            down_name = self.normalize_node_name(
                self.from_mtlx_name(elem_down.getName())
            )
            up_name = self.normalize_node_name(
                self.from_mtlx_name(elem_up.getName())
            )
            connect_name = self.normalize_name(elem_connect.getName())

            # Print Element Names
            IO.debug("--- Normalized Element Names ---")
            IO.debug(down_name)
            IO.debug(up_name)
            IO.debug(connect_name)

            # Find or create new nodes
            down_node = self.get_bnode(elem_down)
            up_node = self.get_bnode(elem_up)
            down_port_idx = int(elem_down.getChildIndex(
                elem_connect.getName()))

            # Print Connection Data
            IO.debug("--- Blender Nodes and Connection ---")
            IO.debug("New Connection: \n "
                     "Upstream Node <%s> & Socket <%s> | TO | "
                     "Downstream Node <%s> & Socket <%s> " %
                     (
                         up_node.name,
                         up_node.outputs[0].name,
                         down_node.name,
                         down_node.inputs[down_port_idx].name)
                     )
            IO.debug("--- Connection Data ---")
            IO.debug("Connection Input Name: %s" % elem_connect.getName())
            IO.debug("Connection Input Index: %s" % down_port_idx)

            self.read_material.node_tree.links.new(
                up_node.outputs[0],
                down_node.inputs[down_port_idx])
            self.iter_upstream(elem_connect, mtlx_mat)


    def set_bnode_inputs(self, inputs, bnode):
        """
        Set socket values for input sockets of a Blender Node
        :param inputs: input_sockets
        :type inputs: bpy.types.NodeSocket
        
        :param bnode: Blender Node
        :type bnode: bpy.types.Node
        
        :return: 
        """
        for node_in in inputs:
            self.set_socket_value(node_in, bnode)


    def set_bnode_params(self, params, bnode):
        """
        Set parameter values for parameters of a Blender Node
        :param params: input_sockets
        :type params: bpy.types.NodeSocket

        :param bnode: Blender Node
        :type bnode: bpy.types.Node

        :return: 
        """
        for node_param in params:
            self.set_param_value(node_param, bnode)


    def get_bnode(self, elem):
        """
        Find or create a blender node from a passed in MaterialX Element
        
        :param elem: element
        :type elem: MaterialX.Element
        
        :return: Blender Node
        :rtype: bpy.types.Node
        """
        from .extension_defs import get_node_class_name
        nodes = self.read_material.node_tree.nodes
        # Check for an existing node in the node tree
        b_node = nodes.get(self.normalize_node_name(
            self.from_mtlx_name(elem.getName())), None)
        if b_node is None:
            # Get Blender Information using class id using nodedef name
            node_def = self.read_document.getMatchingNodeDefs(
                self.clean_name(elem.getName()))[0]
            # Get the node's idname
            node_idname = get_node_class_name(node_def.getName())
            # Create a new node
            b_node = self.create_bnode(node_idname, elem)
        return b_node


    def create_bnode(self, idname, elem):
        """
        Create a new Blender Node from a passed in MaterialX.Element
        
        :param idname: Blender Node bl_idname
        :type idname: str
        
        :param elem: element
        :type elem: MaterialX.Element
        
        :return: Blender Node
        :rtype: bpy.types.Node
        """
        IO.debug("Creating new node")
        # Create Node
        b_node = self.read_material.node_tree.nodes.new(idname)
        # Set Node Name
        b_node.name = self.normalize_node_name(self.from_mtlx_name(elem.getName()))
        # Set Graph Position
        b_node.location = [float(elem.getAttribute('xpos')),
                           float(elem.getAttribute('ypos'))]

        return b_node


    def copy_network(self):
        """Copy the network."""
        pass


    def deep_copy_network(self):
        """Copy the network. Flatten all inherited and instanced data."""
        pass


    def reset_network(self):
        """Reset this network to it's default state"""
        pass


    def combine_network(self):
        """Combine this network with another network"""
        pass


    def instantiate_network(self):
        """Instantiate this network into another network as group"""
        pass


    def prune_network(self):
        """Remove unused nodes, sockets and UI elements from the Material and Network"""
        pass


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
        """Setup the node, and add it to the MaterialXNetwork()"""
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
        """Set a node's MTLX data"""
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
        if data:
            self.mtlx_node_data.add(data)

    '''-------------------------------------Node Methods-------------------------------'''

    def yield_nodes(self, nodes):
        """Generator to get nodes from the passed in Material Nodes"""
        if nodes is None:
            nodes = self.nodes
        yield from [node for node in nodes]

    def update_nodes(self):
        """Update all nodes in the current node tree """
        for node in self.yield_nodes(self.nodes):
            node.update()
            yield node

    def iter_update_nodes(self):
        """Iterate through all Blender Material Nodes and update them."""
        yield from (node for node in self.update_nodes())

    def connect_nodes(self, node_data):
        """Read a Node's Data and create the proper Node Links for that Node"""
        IO.info("Connecting Current Node: %s" % node_data.mtlx_name)
        # First get active output node and setup it's node links
        output_node = self.active_output
        for link in node_data.node_links:
            if link[2] == node_data.mtlx_name:
                # If this is the TO Node
                graph_node = node_data.mtlx_node_graph.getNode(link[0])
                IO.debug("'--From' Node & Node Link--")
                IO.debug("From Node: %s" % graph_node)
                IO.debug("Link: %s:" % repr(link))
                IO.debug("To Node: %s" % node_data.mtlx_graph_node)
                IO.debug("Graph Node Inputs: %s" %
                         [i.getName() for i in node_data.mtlx_graph_node.getInputs()])
                # socket_name = (str(link[3]).replace(" ", "_")).lower()
                socket_name = str(link[3])
                IO.debug("--Current Socket & Name--")
                IO.debug("Socket Name: %s" % socket_name)
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
        :param links: Blender Material Node Links
        :returns link_tuple generator
        :rtype: link_tuple(from_node, from_socket, to_node, to_socket)
        """
        # Get Node Names and MTLX Names of sockets.
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

    def yield_sockets(self):
        """Yield a combined list of all sockets"""
        sockets = [([i for i in list(node.inputs)]) + ([o for o in list(node.outputs)])
                   for node in self.nodes]
        yield sockets

    def yield_socket_names(self, node, type):
        """Yield all socket names"""
        if type == 'inputs':
            if len(node.inputs) > 0:
                yield from [i.name for i in node.inputs]
        elif type == 'outputs':
            if len(node.outputs) > 0:
                yield from [o.name for o in node.outputs]


    def get_sockets(self):
        """Return a list of sockets in the pattern (node, name, type)"""
        sockets = []
        for node in self.nodes:
            # Loop through sockets, append socket.mtlx_name to lists
            for socket_name in self.yield_socket_names(node, 'inputs'):
                sockets.append((node, socket_name, 'input'))
            for socket_name in self.yield_socket_names(node, 'outputs'):
                sockets.append((node, socket_name, 'output'))
        return sockets

    def increment_socket(self, count):
        """Increment the Node Socket name based on the current count"""
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
        """Count the total number of sockets in the node tree to create unique sockets"""
        count = 0
        for node in self.nodes:
            if len(node.inputs) > 0:
                for i_socket in node.inputs:
                    count += 1
            if len(node.outputs) > 0:
                for o_socket in node.outputs:
                    count += 1
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
            param_name = node_param.getName()
            param_type = node_param.getType()
            param_value = node_param.getValue()
            # Set the Blender Node parameter
            if param_type == 'string':
                try:
                    setattr(b_node, param_name, param_value)
                except TypeError:
                    IO.error("Cannot set the Node's attribute. \n "
                          "Node: %s.%s; Continuing..." %
                          (b_node.name, param_name))
                    pass
            elif 'float' in param_type:
                setattr(b_node, param_name,
                        float(param_value))
                return
            elif 'vector' in param_type:
                setattr(b_node, param_name,
                        [float(x) for x in param_value])
                return
            elif 'color' in param_type:
                setattr(b_node, param_name,
                        [float(x) for x in param_value])
                return
            elif param_type == 'filename':
                if param_value == '':
                    IO.warning("%s.%s is null. "
                               "Skipping image load" %
                        (b_node.name, param_name))
                    return
                else:
                    IO.warning("Need to load external file: %s" %
                           os.path.basename(param_value))

                    image = bpy.data.images.load(param_value, check_existing=True)
                    b_node.image = image
                    return
        else:
            IO.warning("Parameter {} not found for node {}".format(
                node_param.getName(), b_node.name))

    '''-----------------------------------Special Methods--------------------------------'''

    def reset_mtlx_names(self):
        """Reset all assigned mtlx_names"""
        for node in self.nodes:
            for input in node.inputs:
                input.mtlx_name = ""
            for output in node.outputs:
                output.mtlx_name = ""

    @staticmethod
    def join_document(cls, mtlx_doc):
        """Joins the passed mtlx_doc with an initialized document"""
        # Initialize the network, pass the class doc by reference to a temp_doc variable
        temp_doc = cls.document
        # Grab a pointer reference to the Document() element of a MaterialX document
        doc_ptr = mtlx_doc.getDocument()
        # Copy the doc_ptr's content to the temp_doc
        temp_doc.copyContentFrom(doc_ptr)
        # Create a joined document and return it from this function
        join_doc = temp_doc
        return join_doc

    @classmethod
    def set_node_location(cls, material, node, loc):
        """Set a physical node location in blender"""
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
        """Check the current render engine"""
        if self.render_engine is None:
            self.render_engine = bpy.context.scene.render.engine

    @property
    def sockets(self):
        return self._sockets
    @sockets.setter
    def sockets(self, value):
        self._sockets = value

    @classmethod
    def increment_name(cls, name):
        return StringResolver.increment_name(name)

    @classmethod
    def to_mtlx_name(cls, name):
        return StringResolver.to_mtlx_name(name)

    @classmethod
    def from_mtlx_name(cls, name):
        return StringResolver.from_mtlx_name(name)

    @classmethod
    def normalize_name(cls, name):
        return StringResolver.normalize_name(name)

    @classmethod
    def clean_name(cls, name):
        return StringResolver.clean_name(name)

    @classmethod
    def normalize_node_name(cls, name):
        return StringResolver.normalize_node_name(name)

    @classmethod
    def mtlx_id_name(cls, name):
        return StringResolver.mtlx_id_name(name)

    @classmethod
    def get_node_def(cls, document, name):
        return document.getNodeDef(str(name).lower())

class StringResolver(object):
    """
    Handler class for String parsing.
    This class defines a set of methods for the purpose of handing various string naming
     operations.
    Extensions to this class should revolve around modifying and cleaning up the current
    methods, while adding new ones to produce larger case coverage.
    """

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
        """Creates a correct MTLX name"""
        return (str(name).lower()).replace(" ", "_")

    @classmethod
    def mtlx_id_name(cls, name):
        from .extension_defs import get_node_class_name
        return get_node_class_name(name)

    @classmethod
    def from_mtlx_name(cls, name):
        """Deserialzie a proper MTLX name"""
        return (str(name).replace("_", " ")).title()

    @classmethod
    def normalize_name(cls, name):
        """Reformat an incremented name and replace underscores with whitespace"""
        name = cls.clean_name(name)
        new_name = " ".join([n.capitalize() for n in name.split("_")])
        return new_name

    @classmethod
    def normalize_node_name(cls, name):
        if 'Bsdf' in name:
            name = name.replace(name.split(" ")[1], name.split(" ")[1].upper())
        return name

    @classmethod
    def clean_name(cls, name):
        """Remove increment from name"""
        name = name.split(".", 1)[0]
        return name

    @classmethod
    def normalize_camel_case(cls, name):
        """Deserialie a proper MTLX name"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def register():
    """Blender's register function. Injects methods and classes into Blender"""
    bpy.types.Material.mtlx_network = MaterialXNetwork()


def unregister():
    """Blender's unregister function. Removes methods and classes from Blender"""
    del bpy.types.Material.mtlx_network