# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    Installs required python packages for this addon

:description:
    

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import os
from os.path import join
import bpy
from .. import conf
from .. utils.io import catch_registration_error, IO, Autovivification
from .preferences import getPreferences
import subprocess
import shutil
import platform

resource_path = bpy.utils.resource_path('LOCAL',
                                        major=bpy.app.version[0],
                                        minor=bpy.app.version[1])
user_path = bpy.utils.resource_path('USER',
                                    major=bpy.app.version[0],
                                    minor=bpy.app.version[1])
bpy_dir = os.path.join(resource_path, 'python')
config_dir = os.path.join(user_path, 'scripts/config')
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#


def run_command_popen(cmd):
    sp = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if err:
        print("__________________________")
        print("Subprocess standard error:")
        print(err.decode('ascii'))
        # sp.wait()


# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class InstallMaterialX(bpy.types.Operator):
    bl_idname = "install.materialx"
    bl_label = "Install MaterialX"
    bl_options = {'REGISTER'}

    def execute(self, context):
        #Resource and User Paths for installing libraries into the user's blender
        local_path = bpy.utils.resource_path('LOCAL',
                                             major=bpy.app.version[0],
                                             minor=bpy.app.version[1])
        site_packages = os.path.join(bpy_dir, 'lib', 'python3.5', 'site-packages')
        # Climb up path
        uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
        addon_path = uppath(__file__, 2)
        # Library Directory
        dist_dir = os.path.join(addon_path, "lib", 'dist')
        if platform.system() == 'windows':
            matx_lib = os.path.join(dist_dir, 'windows', 'MaterialX.zip')
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            # Check for Admin Privileges
            if is_admin is False:
                self.report({'ERROR'}, "Cannot Install MaterialX. "
                                       "Run Blender as an Administrator")
            # Unpack the library to the blender installation from config
            shutil.unpack_archive(matx_lib, site_packages)
        else:
            # Unpack the library to the blender installation from config
            matx_lib = os.path.join(dist_dir, 'linux', 'MaterialX.tar.xz')
            shutil.unpack_archive(matx_lib, site_packages)

        IO.info("MaterialX unpacked and installed here: %s" % site_packages)

        # After installtion, set install flags to disable the operator via poll
        # conf.materialx_lib = True
        scn = context.scene
        libs = scn.material_pipeline_libs
        libs.materialx_lib = True
        self.report({'INFO'}, "MaterialX Installed")

        return {'FINISHED'}


class InstallRequirements(bpy.types.Operator):
    bl_idname = "install.mtlx_requirements"
    bl_label = "Install Requirements"
    bl_options = {'REGISTER'}

    def execute(self, context):
        """Installs requirements.txt and Pysbs"""
        if conf.py_reqs is True:
            self.report({'INFO'}, "Addon Package Already Configured")
            return{'CANCELLED'}
        python = bpy.app.binary_path_python
        uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
        req_file = join(uppath(__file__, 2), 'requirements.txt')
        command = [
            python,
            '-m'
            'pip',
            'install',
            "-r", req_file
        ]
        return {'FINISHED'}

class MaterialPipelineLibraries(bpy.types.PropertyGroup):
    @classmethod
    @catch_registration_error
    def register(cls):
        bpy.types.Scene.material_pipeline_libs = bpy.props.PointerProperty(
            name="Material Pipeline Libraries",
            description='Configured Python Libraries for the Material Pipeline',
            type=cls,
        )

        cls.materialx_lib = bpy.props.BoolProperty(
            name="MaterialX Library",
            description="Flag to check for MaterialX Library",
            default=False,
        )

    @classmethod
    @catch_registration_error
    def unregister(cls):
        del bpy.types.Scene.material_pipeline_libs

# ---------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------- REGISTER --#


