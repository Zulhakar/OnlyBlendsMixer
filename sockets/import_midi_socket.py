import bpy
from ..config import COLOR_STRING_SOCKET, IMPORT_ICON
from ..base.global_data import Data
from ..cnt.sockets.basic_sockets import NodeTreeInterfaceSocketCnt, NodeSocketCnt


class NodeSocketImportMidi(NodeSocketCnt):
    """Midi Import Socket"""
    bl_label = "MIDI Import Socket"
    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop(), name="Import MIDI")
    sock_col = COLOR_STRING_SOCKET

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            r = layout.row(align=True)
            r.prop(self, 'input_value', text="", placeholder='Path')
            d = r.operator(Data.uuid_operator_class_storage[node.node_uuid].bl_idname, icon=IMPORT_ICON, text="")


class NodeTreeInterfaceSocketImportMidi(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketImportMidi'

    def draw_color(self, context, node):
        return COLOR_STRING_SOCKET
