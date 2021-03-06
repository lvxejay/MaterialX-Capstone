import bpy
from bpy.props import *

from .. import conf

addonName = "materialx-blender"

class MaterialPipelinePreferences(bpy.types.AddonPreferences):
    bl_idname = addonName

    # # -------------updater settings -----------------------
    # auto_check_update = bpy.props.BoolProperty(
    #     name="Auto-check for Update",
    #     description="If enabled, auto-check for updates using an interval",
    #     default=True,
    # )
    # updater_intrval_months = bpy.props.IntProperty(
    #     name='Months',
    #     description="Number of months between checking for updates",
    #     default=0,
    #     min=0
    # )
    # updater_intrval_days = bpy.props.IntProperty(
    #     name='Days',
    #     description="Number of days between checking for updates",
    #     default=1,
    #     min=0,
    # )
    # updater_intrval_hours = bpy.props.IntProperty(
    #     name='Hours',
    #     description="Number of hours between checking for updates",
    #     default=0,
    #     min=0,
    #     max=23
    # )
    # updater_intrval_minutes = bpy.props.IntProperty(
    #     name='Minutes',
    #     description="Number of minutes between checking for updates",
    #     default=0,
    #     min=0,
    #     max=59
    # )

    def draw(self, context):
        pcoll = conf.preview_collections["icons"]
        matx_icon = pcoll["matx"]
        preferences = context.user_preferences.addons['materialx-blender'].preferences
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator('install.mtlx_requirements', icon='DISK_DRIVE')
        row.operator("install.materialx", icon_value=matx_icon.icon_id)
        row.scale_y = 2.5
        layout.separator()


def getPreferences():
    """Utility function to get Addon Preferences"""
    return bpy.context.user_preferences.addons["materialx-blender"].preferences

