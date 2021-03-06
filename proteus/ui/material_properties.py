# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    Blender Python API declared properties and settings

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
from ...utils.io import catch_registration_error
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class MaterialXProperties(bpy.types.PropertyGroup):
    @classmethod
    @catch_registration_error
    def register(cls):
        bpy.types.Material.mtlx_props = bpy.props.PointerProperty(
            name="",
            description='MaterialX Properties',
            type=cls,
            # options={'HIDDEN'}
        )
        cls.doc_write = bpy.props.StringProperty(
            name='Write Path',
            description='MaterialX Document Write Filepath',
            subtype='FILE_PATH'
        )
        cls.doc_read = bpy.props.StringProperty(
            name='Read Path',
            description='MaterialX Document Read Filepath',
            subtype='FILE_PATH'
        )

    @classmethod
    @catch_registration_error
    def unregister(cls):
        del bpy.types.Material.mtlx_props


class MaterialXPanel(bpy.types.Panel):
    bl_label = "Material X"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        mat_idx = context.active_object.active_material_index
        material = context.active_object.material_slots[mat_idx].material
        layout = self.layout
        row = layout.row()
        row.prop(material.mtlx_props, 'doc_write', text='Write Path')
        row = layout.row()
        row.prop(material.mtlx_props, 'doc_read', text='Read Path')
        row = layout.row()
        row.operator('mtlx_operator.write')
        row = layout.row()
        row.operator('mtlx_operator.read')

