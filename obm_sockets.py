import bpy

from .constants import IMPORT_ICON, COLOR_STRING_SOCKET, COLOR_SOUND_SAMPLE_SOCKET, COLOR_DEVICE_SOCKET
from .global_data import Data

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


class NodeTreeInterfaceSocketWavImport(bpy.types.NodeTreeInterfaceSocket):
    # The type of socket that is generated.
    bl_socket_idname = 'WavImportSocketType'

    default_value: bpy.props.StringProperty()

    def draw(self, context, layout):
        # Display properties of the interface.
        layout.prop(self, "default_value")

    # Set properties of newly created sockets
    def init_socket(self, node, socket, data_path):
        # socket.display_shape = "SQUARE"
        socket.input_value = self.default_value
        print("init_socket")

    # Use an existing socket to initialize the group interface
    def from_socket(self, node, socket):
        # Current value of the socket becomes the default
        self.default_value = socket.input_value
        print("from_socket")


class SoundSampleSocket(bpy.types.NodeSocket):
    """Obm Object Socket"""
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SoundSampleSocketType'
    # Label for nice name display
    bl_label = "Sound Sample Socket"

    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_path_action())

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def update_path_action(self):
        print("SoundSampleSocketType: input_value update")
        print(self.input_value)

    def poll(self, other_socket):
        # Entscheidet, ob Verbindung erlaubt ist
        ttt = getattr(other_socket, "socket_type", None) == self.input_value
        print(ttt)
        return ttt

    @classmethod
    def draw_color_simple(cls):
        # cls.display_shape = "SQUARE"
        return COLOR_SOUND_SAMPLE_SOCKET


class NodeTreeInterfaceSocketSoundSample(bpy.types.NodeTreeInterfaceSocket):
    # The type of socket that is generated.
    bl_socket_idname = 'SoundSampleSocketType'

    default_value: bpy.props.StringProperty()

    def draw(self, context, layout):
        # Display properties of the interface.
        layout.prop(self, "default_value")

    # Set properties of newly created sockets
    def init_socket(self, node, socket, data_path):
        # socket.display_shape = "SQUARE"
        socket.input_value = self.default_value
        print("init_socket")

    # Use an existing socket to initialize the group interface
    def from_socket(self, node, socket):
        # Current value of the socket becomes the default
        self.default_value = socket.input_value
        print("from_socket")


class DeviceSocket(bpy.types.NodeSocket):
    """Obm Object Socket"""
    bl_idname = 'DeviceSocketType'
    bl_label = "Device Socket"

    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_path_action())

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def update_path_action(self):
        print("DeviceSocketType: input_value update")

    @classmethod
    def draw_color_simple(cls):
        # cls.display_shape = "SQUARE"
        return COLOR_DEVICE_SOCKET


class NodeTreeInterfaceSocketDevice(bpy.types.NodeTreeInterfaceSocket):
    # The type of socket that is generated.
    bl_socket_idname = 'DeviceSocketType'

    default_value: bpy.props.StringProperty()

    def draw(self, context, layout):
        # Display properties of the interface.
        layout.prop(self, "default_value")

    # Set properties of newly created sockets
    def init_socket(self, node, socket, data_path):
        # socket.display_shape = "SQUARE"
        socket.input_value = self.default_value
        print("init_socket")

    # Use an existing socket to initialize the group interface
    def from_socket(self, node, socket):
        # Current value of the socket becomes the default
        self.default_value = socket.input_value
        print("from_socket")
