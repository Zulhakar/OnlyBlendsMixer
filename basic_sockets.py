import bpy

from .constants import (COLOR_OBJECT_SOCKET, COLOR_BLACK, COLOR_STRING_SOCKET, COLOR_INT_SOCKET, COLOR_FLOAT_SOCKET,
                        COLOR_EMPTY_SOCKET)
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

classes = (NodeTreeInterfaceSocketSound, SoundSocket, NodeTreeInterfaceSocketObject, ObjectSocket ,
           NodeTreeInterfaceSocketObmFloat, ObmFloatSocket, NodeTreeInterfaceSocketObmInt, ObmIntSocket,
           ObmStringSocket, NodeTreeInterfaceSocketObmString)

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
           ObmEmptySocket, NodeTreeInterfaceSocketObmEmpty
           )


# def create_basic_socket(class_name, class_type, bl_idname, bl_label, sock_col=COLOR_BLACK):
#     @classmethod
#     def draw_color_simple(cls):
#         # cls.display_shape = "SQUARE"
#         return cls.sock_col
#
#     ObmBasicSocketClass = type(class_name, (ObmBasicSocket, NodeSocket), {
#         "bl_label": bl_label,
#         "bl_idname": bl_idname,
#         "sock_col": sock_col,
#         "draw_color_simple": draw_color_simple,
#         "input_value": bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name=class_name,
#                                                  type=class_type)
#     })
#     return ObmBasicSocketClass


#class_name, class_type = "ObmObjectSocket", bpy.types.Object
#ObmObjectSocket = create_basic_socket(class_name, class_type, "ObmObjectSocketType", "Object Socket")
#class_name, class_type = "SoundSocket", bpy.types.Sound
#SoundSocket = create_basic_socket(class_name, class_type, "SoundSocketType", "Sound Socket")

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