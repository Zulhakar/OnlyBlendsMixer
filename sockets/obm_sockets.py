import bpy

from ..core.constants import IMPORT_ICON, COLOR_STRING_SOCKET, COLOR_DEVICE_SOCKET
from ..core.global_data import Data
from .basic_sockets import ObmNodeTreeInterfaceSocket


class WavImportSocket(bpy.types.NodeSocket):
    """Obm Object Socket"""
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'WavImportSocketType'
    # Label for nice name display
    bl_label = "Wav Import Socket"
    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_path_action())

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):

        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            r = layout.row(align=True)
            r.prop(self, 'input_value', text="", placeholder='Path')
            d = r.operator(Data.uuid_operator_class_storage[node.node_uuid].bl_idname, icon=IMPORT_ICON, text="")
            # self.input_value = d.filepath

    def update_path_action(self):
        print("WavImportSocketType: input_value update")

    @classmethod
    def draw_color_simple(cls):
        # cls.display_shape = "SQUARE"
        return COLOR_STRING_SOCKET


class NodeTreeInterfaceSocketWavImport(ObmNodeTreeInterfaceSocket):
    # The type of socket that is generated.
    bl_socket_idname = 'WavImportSocketType'


class DeviceSocket(bpy.types.NodeSocket):
    """Obm Object Socket"""
    bl_idname = 'DeviceSocketType'
    bl_label = "Device"

    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_path_action())
    value: bpy.props.StringProperty(update=lambda self, context: self.update_path_action())

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def update_path_action(self):
        print("DeviceSocketType: input_value update")

    @classmethod
    def draw_color_simple(cls):
        # cls.display_shape = "SQUARE"
        return COLOR_DEVICE_SOCKET

    def draw_color(self, context, node):
        return COLOR_DEVICE_SOCKET


class NodeTreeInterfaceSocketDevice(ObmNodeTreeInterfaceSocket):
    # The type of socket that is generated.
    bl_socket_idname = 'DeviceSocketType'

    def draw_color(self, context, node):
        # cls.display_shape = "SQUARE"
        return COLOR_DEVICE_SOCKET
