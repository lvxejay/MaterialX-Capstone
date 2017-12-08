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

from ..properties.dynamic_property import dynamic, node_parameter
from ..base_types.base_socket import to_socket_id
from ...utils.enum_items import enumItemsFromList
from ...utils.io import catch_registration_error

socket_types = ['Custom', 'Value', 'Int', 'Boolean',
                    'Vector', 'String', 'RGBA', 'Shader']
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def get_socket_types(self, context):
    items = enumItemsFromList(socket_types)
    return items
# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#
class SocketParameter(object):
    def __init__(self, socket, **kwargs):
        self.id = to_socket_id(socket)
        self.identifier = self.id[2]
        self.type = socket.type
        self.param_type = kwargs.setdefault("param_type", "NodeSocketParameters")
        self._prop_dict = {}
        self._property = None
        self._property_group = None
        self._blender_type = bpy.types.NodeTree
        self._socket = socket

    @staticmethod
    @node_parameter
    def convert_value(value, **kwargs):
        return value

    @staticmethod
    @dynamic
    def create_property_group(prop_dict, **kwargs):
        return prop_dict

    @property
    def prop_dict(self):
        self._prop_dict[self.identifier] = self.blender_prop
        return self._prop_dict

    @property
    def default_value(self):
        if hasattr(self._socket, "default_value"):
            return self._socket.default_value
        else:
            return None

    @property
    def blender_prop(self):
        """Return bpy.Prop Function"""
        self._property = self.convert_value(self.default_value, type=self.type)
        return self._property

    @property
    def blender_prop_type(self):
        return repr(self.blender_prop[0])

    @property
    def socket_value(self):
        return self.blender_prop[1].get("default")

    @property
    def blender_prop_group(self):
        self._property_group = self.create_property_group(
            self.prop_dict, blender_type=self._blender_type, param_type=self.param_type
        )
        return self._property_group


def update_type(self, context):
    print("Update Called with self = %s" % (self))
    test = repr(self)
    string = test.rsplit(".", 1)
    print(string)

class NodeSocketParameters(bpy.types.PropertyGroup):
    @classmethod
    @catch_registration_error
    def register(cls):
        bpy.types.NodeSocket.parameters = PointerProperty(
            type=cls,
            name='Socket Parameters',
            description='Socket Parameters'
        )
        cls.exposed = BoolProperty(default=False)
        cls.type = EnumProperty(items=get_socket_types, update=update_type)
        cls.identifier = StringProperty()

    @classmethod
    @catch_registration_error
    def unregister(cls):
        del bpy.types.NodeSocket.parameters



class ParameterCollection(bpy.types.PropertyGroup):
    @classmethod
    @catch_registration_error
    def register(cls):
        bpy.types.Scene.exposed_parameters = PointerProperty(
            type=cls,
            name='Exposed Parameters List',
            description='Exposed Parameters List',
            options={'HIDDEN'}
        )
        cls.exposed = BoolProperty(default=True)
        cls.type = StringProperty()
        cls.identifier = StringProperty()

    @classmethod
    @catch_registration_error
    def unregister(cls):
        del bpy.types.Scene.exposed_parameters

class NodeTreeParameters(bpy.types.PropertyGroup):
    @classmethod
    @catch_registration_error
    def register(cls):
        bpy.types.NodeTree.parameters = PointerProperty(
            type=cls,
            name='Node Parameters',
            description='Node Parameters',
        )
        cls.exposed = CollectionProperty(name='Exposed Parameters',
                                         type=ParameterCollection)

    @classmethod
    @catch_registration_error
    def unregister(cls):
        del bpy.types.NodeTree.parameters


class MaterialParameters(bpy.types.PropertyGroup):
    @classmethod
    @catch_registration_error
    def register(cls):
        bpy.types.Material.parameters = PointerProperty(
            type=cls,
            name='Material Parameters',
            description='Material Parameters',
        )
        cls.exposed = CollectionProperty(name='Exposed Parameters',
                                         type=ParameterCollection)

    @classmethod
    @catch_registration_error
    def unregister(cls):
        del bpy.types.Material.parameters


class MaterialParameterPanel(bpy.types.Panel):
    bl_label = "Exposed Parameters"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    # bl_context = "material"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.scale_y = 1.5

