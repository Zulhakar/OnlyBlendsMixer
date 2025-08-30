import bpy

from .constants import (COLOR_OBJECT_SOCKET, COLOR_BLACK, COLOR_STRING_SOCKET, COLOR_INT_SOCKET, COLOR_FLOAT_SOCKET,
                        COLOR_EMPTY_SOCKET, COLOR_BOOL_SOCKET)
from bpy.types import NodeSocket, NodeTreeInterfaceSocket
from bpy.utils import (register_class,
                       unregister_class)


class ObmBasicSocket(NodeSocket):

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "input_value", text=text)

    def update_prop(self):
        print("Prop update")
        print(self.input_value)
        if hasattr(self.node, "socket_update"):
            self.node.socket_update(self)

class ObmNodeTreeInterfaceSocket(NodeTreeInterfaceSocket):
    default_value: None

    def draw(self, context, layout):
        layout.prop(self, "default_value")

    def init_socket(self, node, socket, data_path):
        socket.input_value = self.default_value
        print("init_socket")

    def from_socket(self, node, socket):
        self.default_value = socket.input_value
        print("from_socket")

class NodeTreeInterfaceSocketSound(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'SoundSocketType'

class SoundSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'SoundSocketType'
    bl_label = "Sound Socket"
    sock_col = COLOR_BLACK

    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Sound",
                                           type=bpy.types.Sound)  # poll=poll_domain)
    # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

class NodeTreeInterfaceSocketObject(ObmNodeTreeInterfaceSocket, NodeTreeInterfaceSocket):
    bl_socket_idname = 'SoundSocketType'

class ObjectSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'ObjectSocketType'
    bl_label = "Object Socket"
    sock_col = COLOR_OBJECT_SOCKET

    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Object",
                                           type=bpy.types.Object)  # poll=poll_domain)

   # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

class NodeTreeInterfaceSocketObmFloat(ObmNodeTreeInterfaceSocket, NodeTreeInterfaceSocket):
    bl_socket_idname = 'FloatSocketType'

class ObmFloatSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'FloatSocketType'
    bl_label = "Float"
    sock_col = COLOR_FLOAT_SOCKET

    input_value: bpy.props.FloatProperty(update=lambda self, context: self.update_prop(), name="Float")

   # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

class NodeTreeInterfaceSocketObmInt(ObmNodeTreeInterfaceSocket, NodeTreeInterfaceSocket):
    bl_socket_idname = 'IntSocketType'

class ObmIntSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'IntSocketType'
    bl_label = "Integer"
    sock_col = COLOR_INT_SOCKET

    input_value: bpy.props.IntProperty(update=lambda self, context: self.update_prop(), name="Integer")

   # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

class NodeTreeInterfaceSocketObmString(ObmNodeTreeInterfaceSocket, NodeTreeInterfaceSocket):
    bl_socket_idname = 'StringSocketType'

class ObmStringSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'StringSocketType'
    bl_label = "String"
    sock_col = COLOR_STRING_SOCKET

    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop(), name="String")

   # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

class NodeTreeInterfaceSocketObmBool(ObmNodeTreeInterfaceSocket, NodeTreeInterfaceSocket):
    bl_socket_idname = 'BoolSocketType'

class ObmBoolSocket(ObmBasicSocket):
    """Boolean Socket Type"""
    bl_idname = 'BoolSocketType'
    bl_label = 'Bool'
    sock_col = COLOR_BOOL_SOCKET

    input_value: bpy.props.BoolProperty(update=lambda self, context: self.update_prop(), name="Bool")

   # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col


class NodeTreeInterfaceSocketObmEmpty(ObmNodeTreeInterfaceSocket, NodeTreeInterfaceSocket):
    bl_socket_idname = 'EmptySocketType'

class ObmEmptySocket(NodeSocket):
    """Sound Socket to play"""
    bl_idname = 'EmptySocketType'
    bl_label = "Empty"
    sock_col = COLOR_EMPTY_SOCKET

   # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

    def draw(self, context, layout, node, text):
        pass


classes = (NodeTreeInterfaceSocketSound, SoundSocket, NodeTreeInterfaceSocketObject, ObjectSocket ,
           NodeTreeInterfaceSocketObmFloat, ObmFloatSocket, NodeTreeInterfaceSocketObmInt, ObmIntSocket,
           ObmStringSocket, NodeTreeInterfaceSocketObmString,
           ObmEmptySocket, NodeTreeInterfaceSocketObmEmpty,
           ObmBoolSocket, NodeTreeInterfaceSocketObmBool
           )


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except Exception as e:
            print(e)
            print(cls)