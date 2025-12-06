import bpy
from bpy.types import NodeSocket, NodeTreeInterfaceSocket
from bpy.utils import (register_class,
                       unregister_class)
from ..core.constants import (COLOR_OBJECT_SOCKET, COLOR_BLACK, COLOR_STRING_SOCKET, COLOR_INT_SOCKET, COLOR_FLOAT_SOCKET,
                            COLOR_FLOAT_VECTOR_SOCKET,
                            COLOR_EMPTY_SOCKET, COLOR_SPEAKER_SOCKET, COLOR_BOOL_SOCKET, COLOR_SOUND_SAMPLE_SOCKET, IS_DEBUG)

from ..helper import get_socket_index

class ObmBasicSocket(NodeSocket):
    is_constant: bpy.props.BoolProperty()
    group_node_tree_name: bpy.props.StringProperty()
    group_node_name: bpy.props.StringProperty()
    def draw(self, context, layout, node, text):
        if self.is_constant:
            layout.alignment = 'EXPAND'
            layout.prop(self, "input_value", text="")
        else:
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                layout.prop(self, "input_value", text=text)

    def update_prop(self):
        if IS_DEBUG:
            log_string = f"{self.node.bl_idname}-> Socket: {self.bl_idname} update_prop: [name: {self.name},  value: {self.input_value}]"
            print(log_string)
        if hasattr(self.node, "socket_update"):
            self.node.socket_update(self)

        # ----------------------------------------------------------
        # inject update for build in nodes (Group Input/Output Node)
        # maybee pointer for socket group_output inputs with group_node output
        else:
            if self.node.bl_idname == "NodeGroupOutput":
                #get tree -> get group_node -> boom
                if self.group_node_tree_name != "":
                    node = self.node
                    #print("Trigger from Socket")
                    tree = bpy.data.node_groups[self.group_node_tree_name]
                    group_node = tree.nodes[self.group_node_name]
                    #print(group_node.name)
                    sock_index = get_socket_index(node.inputs, self)
                    group_node.outputs[sock_index].input_value = self.input_value
        # ----------------------------------------------------------

    # Socket color
    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col

    # Socket color


class ObmNodeTreeInterfaceSocket(bpy.types.NodeTreeInterfaceSocket):
    default_value: bpy.props.StringProperty()
    def draw(self, context, layout):
        layout.prop(self, "default_value")

    def init_socket(self, node, socket, data_path):
        socket.input_value = self.default_value

    def from_socket(self, node, socket):
        print("from socket")
        # self.default_value = socket.input_value

    def draw_color(self, context, node):
        return COLOR_BLACK


class NodeTreeInterfaceSocketSoundSample(ObmNodeTreeInterfaceSocket):
    # The type of socket that is generated.
    bl_socket_idname = 'SoundSampleSocketType'

    def draw_color(self, context, node):
        # cls.display_shape = "SQUARE"
        return COLOR_SOUND_SAMPLE_SOCKET

class SoundSampleSocket(ObmBasicSocket):
    """Obm Sample Socket"""
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SoundSampleSocketType'
    # Label for nice name display
    bl_label = "Sample"

    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop())

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)


    @classmethod
    def draw_color_simple(cls):
        # cls.display_shape = "SQUARE"
        return COLOR_SOUND_SAMPLE_SOCKET

    def draw_color(self, context, node):
        # cls.display_shape = "SQUARE"
        return COLOR_SOUND_SAMPLE_SOCKET





class NodeTreeInterfaceSocketSound(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'SoundSocketType'


class SoundSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'SoundSocketType'
    bl_label = "Sound"
    sock_col = COLOR_BLACK

    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Sound",
                                           type=bpy.types.Sound)  # poll=poll_domain)

    def draw_color(self, context, node):
        # cls.display_shape = "SQUARE"
        return COLOR_BLACK


class SpeakerSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'SpeakerSocketType'
    bl_label = "Speaker"
    sock_col = COLOR_SPEAKER_SOCKET

    type = "CUSTOM"
    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Speaker",
                                           type=bpy.types.Speaker)  # poll=poll_domain)


class NodeTreeInterfaceSocketSpeaker(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'SpeakerSocketType'

    def draw_color(self, context, node):
        return COLOR_SPEAKER_SOCKET


class ObjectSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'ObjectSocketType'
    bl_label = "Object"
    sock_col = COLOR_OBJECT_SOCKET
    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Object",
                                           type=bpy.types.Object)  # poll=poll_domain)


class NodeTreeInterfaceSocketObject(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'ObjectSocketType'

    def draw_color(self, context, node):
        # cls.display_shape = "SQUARE"
        return COLOR_OBJECT_SOCKET


class ObmFloatSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'FloatSocketType'
    bl_label = "Float"
    sock_col = COLOR_FLOAT_SOCKET

    input_value: bpy.props.FloatProperty(update=lambda self, context: self.update_prop(), name="Float")


class NodeTreeInterfaceSocketObmFloat(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'FloatSocketType'

    def draw_color(self, context, node):
        return COLOR_FLOAT_SOCKET


class ObmFloatVectorSocket(ObmBasicSocket):
    """Float Vector"""
    bl_idname = 'FloatVectorSocketType'
    bl_label = "Float Vector"
    sock_col = COLOR_FLOAT_VECTOR_SOCKET

    input_value: bpy.props.FloatVectorProperty(update=lambda self, context: self.update_prop(), name="FloatVector")

    def draw(self, context, layout, node, text):
        if self.is_constant:
            layout.alignment = 'EXPAND'
            layout.prop(self, "input_value", text="")
        else:
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                layout.prop(self, "input_value", text=text)

class NodeTreeInterfaceSocketObmFloatVector(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'FloatVectorSocketType'

    def draw_color(self, context, node):
        return COLOR_FLOAT_VECTOR_SOCKET


class FloatVectorFieldItem(bpy.types.PropertyGroup):
    # value: bpy.props.FloatVectorProperty(update=lambda self, context: self.update_prop())
    value: bpy.props.FloatVectorProperty()


register_class(FloatVectorFieldItem)


class ObmFloatVectorFieldSocket(ObmBasicSocket):
    """Float Vector"""
    bl_idname = 'FloatVectorFieldSocketType'
    bl_label = "Float Vector Field"
    sock_col = COLOR_FLOAT_VECTOR_SOCKET
    input_value: bpy.props.CollectionProperty(type=FloatVectorFieldItem)
    # input_value: bpy.props.CollectionProperty(update=lambda self, context: self.update_prop(), name="FloatVector")
    # input_value: ()
    # input_value: bpy.props.CollectionProperty(type=bpy.props.FloatVectorProperty)


class NodeTreeInterfaceSocketObmFloatVectorField(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'FloatVectorFieldSocketType'

    def draw_color(self, context, node):
        return COLOR_FLOAT_VECTOR_SOCKET


class ObmIntSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'IntSocketType'
    bl_label = "Integer"
    sock_col = COLOR_INT_SOCKET

    input_value: bpy.props.IntProperty(update=lambda self, context: self.update_prop(), name="Integer")


class NodeTreeInterfaceSocketObmInt(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'IntSocketType'

    def draw_color(self, context, node):
        return COLOR_INT_SOCKET


class ObmStringSocket(ObmBasicSocket):
    """Sound Socket to play"""
    bl_idname = 'StringSocketType'
    bl_label = "String"
    sock_col = COLOR_STRING_SOCKET
    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop(), name="String")


class NodeTreeInterfaceSocketObmString(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'StringSocketType'

    def draw_color(self, context, node):
        return COLOR_STRING_SOCKET


class ObmBoolSocket(ObmBasicSocket):
    """Boolean Socket Type"""
    bl_idname = 'BoolSocketType'
    bl_label = 'Bool'
    sock_col = COLOR_BOOL_SOCKET

    input_value: bpy.props.BoolProperty(update=lambda self, context: self.update_prop(), name="Bool")

    def draw(self, context, layout, node, text):
        layout.alignment = 'LEFT'
        layout.prop(self, "input_value", text=text)


class NodeTreeInterfaceSocketObmBool(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'BoolSocketType'

    def draw_color(self, context, node):
        return COLOR_BOOL_SOCKET


class NodeTreeInterfaceSocketObmEmpty(ObmNodeTreeInterfaceSocket):
    bl_socket_idname = 'EmptySocketType'


class ObmEmptySocket(NodeSocket):
    """Connect a link to create a new socket"""
    bl_idname = 'EmptySocketType'
    bl_label = "Empty"
    sock_col = COLOR_EMPTY_SOCKET

    def draw(self, context, layout, node, text):
        pass


classes = (SoundSocket, NodeTreeInterfaceSocketSound,
           SoundSampleSocket, NodeTreeInterfaceSocketSoundSample,
           ObjectSocket, NodeTreeInterfaceSocketObject,
           ObmFloatSocket, NodeTreeInterfaceSocketObmFloat,
           ObmIntSocket, NodeTreeInterfaceSocketObmInt,

           ObmStringSocket, NodeTreeInterfaceSocketObmString,
           # NodeTreeInterfaceSocketObmEmpty, ObmEmptySocket,
           ObmBoolSocket, NodeTreeInterfaceSocketObmBool,
           SpeakerSocket, NodeTreeInterfaceSocketSpeaker,

           ObmFloatVectorSocket, NodeTreeInterfaceSocketObmFloatVector,
           ObmFloatVectorFieldSocket, NodeTreeInterfaceSocketObmFloatVectorField,

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
    # unregister_class(FloatVectorFieldItem)
