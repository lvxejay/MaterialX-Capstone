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

class MtlxWriteOperator(bpy.types.Operator):
    bl_idname = 'mtlx_operator.write'
    bl_label = 'Write MaterialX'

    def execute(self, context):
        mat_idx = context.active_object.active_material_index
        material = context.active_object.material_slots[mat_idx].material
        network = material.mtlx_network
        network.material = material
        network.init_network()
        network.update_network()

        return {'FINISHED'}