import bpy
from ..cnt.sockets.basic_sockets import NodeTreeInterfaceSocketCnt, NodeSocketCnt
from ..config import COLOR_SOUND_SAMPLE_SOCKET, COLOR_BLACK, COLOR_SPEAKER_SOCKET


class NodeTreeInterfaceSocketSample(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketSample'
    obm_socket_type = bl_socket_idname

    def draw_color(self, context, node):
        return COLOR_SOUND_SAMPLE_SOCKET


class NodeSocketSample(NodeSocketCnt):
    bl_label = "Sample"
    sock_col = COLOR_SOUND_SAMPLE_SOCKET
    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop())

    def draw(self, context, layout, node, text):
        layout.label(text=text)


class NodeTreeInterfaceSocketSound(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketSound'
    obm_socket_type = bl_socket_idname


class NodeSocketSound(NodeSocketCnt):
    bl_label = "Sound"
    sock_col = COLOR_BLACK
    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Sound",
                                           type=bpy.types.Sound)  # poll=poll_domain)

    def draw_color(self, context, node):
        return COLOR_BLACK


class NodeSocketSpeaker(NodeSocketCnt):
    bl_label = "Speaker"
    sock_col = COLOR_SPEAKER_SOCKET
    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Speaker",
                                           type=bpy.types.Speaker)  # poll=poll_domain)


class NodeTreeInterfaceSocketSpeaker(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketSpeaker'

    def draw_color(self, context, node):
        return COLOR_SPEAKER_SOCKET
