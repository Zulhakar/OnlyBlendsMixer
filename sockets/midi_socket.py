import bpy
from ..config import COLOR_MIDI_SOCKET
from ..cnt.sockets.basic_sockets import NodeSocketCnt, NodeTreeInterfaceSocketCnt


class NodeSocketMidi(NodeSocketCnt):
    """Midi Socket"""
    bl_label = "MIDI"
    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop(), name="MIDI")
    sock_col = COLOR_MIDI_SOCKET


class NodeTreeInterfaceSocketMidi(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketMidi'

    def draw_color(self, context, node):
        return COLOR_MIDI_SOCKET
