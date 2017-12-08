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
from ...utils.io import IO


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def dynamic(func):
    """

    @:keyword: dynamic - Function Generator that creates properties for 
                            Blender data types on the fly
    :param func: Function to generate
    :return: dynamic_property(): returns decorated function
    """

    def dynamic_property(*args, **kwargs):
        """

        :param args: first argument is always *prop_dict (from func in outer scope)
        :parameter *prop_dict: One Blender Property Mapped to a dict: 
                    e.g. prop_dict = {'mapname': bpy.props.StringProperty(
                                                            default="some_path_to_map")}
        :param kwargs: specific keywords needed by enclosed methods
        :return: Pointer to newly registered/assigned property
        """
        Prop = type(str("Parameters"), (bpy.types.PropertyGroup,), func(*args))
        bpy.utils.register_class(Prop)
        PropPointer = bpy.props.PointerProperty(name=func(kwargs.get('param_type')),
                                                type=Prop)
        setattr(func(kwargs.get('blender_type')), func(kwargs.get('param_type')),
                PropPointer)
        return PropPointer

    return dynamic_property


def parameter(func):
    def parameter_convert(*args, **kwargs):
        if 'constantValueInt' in func(kwargs.get('type')):
            new_arg = str(func(*args).replace('{}'.format(" "), ",")).split(',')
            if len(new_arg) == 3:
                prop = IntVectorProperty(default=new_arg)
                return prop
            elif len(new_arg) == 1:
                prop = IntProperty(default=int(new_arg[0]))
                return prop
            else:
                pass
        elif 'constantValueFloat' in func(kwargs.get('type')):
            new_arg = str(func(*args).replace('{}'.format(" "), ",")).split(',')
            if len(new_arg) == 3:
                prop = FloatVectorProperty(
                    default=[float(new_arg) for new_arg in new_arg])
                return prop
            elif len(new_arg) == 1:
                prop = FloatProperty(default=float(new_arg[0]))
                return prop
            else:
                pass
        elif 'constantValueBool' in func(kwargs.get('type')):
            if (func(*args)) == '0':
                new_arg = False
                prop = BoolProperty(default=new_arg)
            else:
                new_arg = True
                prop = BoolProperty(default=new_arg)
            return prop
        elif 'constantValueString' in func(kwargs.get('type')):
            new_arg = func(*args)
            prop = StringProperty(default=new_arg)
            return prop
        elif 'color' in func(kwargs.get('type')):
            new_arg = str(func(*args).replace('{}'.format(" "), ",")).split(',')
            size = len(new_arg)
            prop = FloatVectorProperty(default=[float(new_arg) for new_arg in new_arg],
                                       subtype='COLOR_GAMMA',
                                       size=size)
            return prop
        elif func(kwargs.get('type')) is None:
            pass

    return parameter_convert

def node_parameter(func):
    def node_param_convert(*args, **kwargs):
        new_arg = func(*args)
        if 'INT' in func(kwargs.get('type')):
            prop = IntProperty(default=int(new_arg))
            return prop
        elif 'VALUE' in func(kwargs.get('type')):
            prop = FloatProperty(default=float(new_arg))
            return prop
        elif 'BOOL' in func(kwargs.get('type')):
            if (func(*args)) == '0':
                new_arg = False
                IO.debug(new_arg)
                prop = BoolProperty(default=new_arg)
            else:
                new_arg = True
                IO.debug(new_arg)
                prop = BoolProperty(default=new_arg)
            return prop
        elif 'STRING' in func(kwargs.get('type')):
            prop = StringProperty(default=new_arg)
            return prop
        elif 'RGBA' in func(kwargs.get('type')):
            size = len(new_arg)
            prop = FloatVectorProperty(default=[float(new_arg) for new_arg in new_arg],
                                       subtype='COLOR_GAMMA',
                                       size=size)
            return prop
        elif 'VECTOR' in func(kwargs.get('type')):
            size = len(new_arg)
            prop = FloatVectorProperty(default=[float(new_arg) for new_arg in new_arg],
                                       subtype='XYZ',
                                       size=size)
            return prop
        elif func(kwargs.get('type')) is None:
            pass
        else:
            pass

    return node_param_convert




# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

