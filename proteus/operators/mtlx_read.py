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

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class MtlxReadOperator(bpy.types.Operator):
    bl_idname = 'mtlx_operator.read'
    bl_label = 'Read MaterialX'

    def execute(self, context):
        mat_idx = context.active_object.active_material_index
        material = context.active_object.material_slots[mat_idx].material
        network = material.mtlx_network
        # network.read_material = None
        network.material = material
        network.read_network()

        return {'FINISHED'}