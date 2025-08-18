import bpy
from bpy.types import (Node, NodeCustomGroup, NodeTree, NodeSocket, Operator, NodeSocketGeometry,
                       NodeTreeInterfaceSocket, GeometryNodeTree, NodeGroupInput, NodeGroupOutput)
from bl_ui import node_add_menu

from .basic_nodes import IntNode, FloatNode, StringNode, ObjectNode, ObmSoundNode
from .basic_sockets import SoundSocket
from .constants import *
import uuid
from .global_data import Data
import aud


# Implementation of custom nodes from Python
def handle_muted_node(node):
    """
    Implements Blender-like bypass behavior for muted nodes.
    Each output will receive the value from the corresponding input if available,
    or fall back to input[0], or finally to 0.
    """
    # print(f"[Muted] Node '{node.name}' is bypassed.")

    for i, output_socket in enumerate(node.outputs):
        value = 0  # Fallback value

        # Prefer corresponding input socket
        if i < len(node.inputs) and node.inputs[i].is_linked:
            value = get_socket_value(node.inputs[i])

        # Fallback to input[0] if it's linked
        elif len(node.inputs) > 0 and node.inputs[0].is_linked:
            value = get_socket_value(node.inputs[0])

        output_socket.default_value = value
    #   print(f" → Output[{i}] = {value}")


# def get_socket_value(socket: NodeSocket):
#     """
#     Retrieves the value from a socket, recursively following links (e.g., through Reroute nodes).
#     It fetches the *actual* data value from the source of the link or the socket's default value.
#     Converts the value to the expected type based on the target socket's type.
#     """
#     current_socket = socket
#
#     # Traverse through linked sockets until we find the actual data source
#     # or an unlinked socket
#     while current_socket.is_linked:
#         from_socket = current_socket.links[0].from_socket
#
#         # If the 'from_socket' is an output of a Reroute node,
#         # we need to go to its input to find the true source.
#         # Otherwise, the from_socket itself is our next candidate.
#         if hasattr(from_socket.node, 'bl_idname') and from_socket.node.bl_idname == 'NodeReroute':
#             # A Reroute node's output socket doesn't hold a value directly.
#             # Its value comes from its *single input socket*.
#             # So, we set the current_socket to the Reroute's input socket
#             # to continue tracing the connection backward.
#             if from_socket.node.inputs[0].is_linked:
#                 current_socket = from_socket.node.inputs[0].links[0].from_socket
#             else:
#                 # Reroute node's input is not linked, so it provides no value
#                 current_socket = None  # Break the loop, effectively meaning no value
#                 break
#         else:
#             # If it's not a Reroute node, then this 'from_socket' is our actual source.
#             current_socket = from_socket
#             break  # Found the source, exit the loop
#
#     val = None
#     if current_socket:
#         # Now current_socket should be the source socket
#         if hasattr(current_socket, "default_value"):
#             val = current_socket.default_value
#
#     # --- Type Conversion based on Target Socket Type ---
#
#     if val is not None:
#         if isinstance(socket, (NodeSocketFloat)):
#             if isinstance(val, (tuple, list, bpy.types.bpy_prop_array)) and hasattr(val, '__len__') and len(val) > 0:
#                 # Take the first component if it's an array/tuple (e.g., from a vector or color output)
#                 return float(val[0])  # type: ignore
#
#             return float(val) if val is not None else 0.0
#
#         elif isinstance(socket, (NodeSocketInt)):
#             if isinstance(val, (tuple, list, bpy.types.bpy_prop_array)) and hasattr(val, '__len__') and len(val) > 0:
#                 return int(val[0])  # type: ignore
#
#             return int(val) if val is not None else 0
#
#         elif isinstance(socket, (NodeSocketColor)):
#             if isinstance(val, (tuple, list, bpy.types.bpy_prop_array)):
#                 if len(val) == 3:
#                     return (*val, 1.0)  # Add default alpha
#                 elif len(val) == 4:
#                     return tuple(val)
#                 return val if val is not None else (0.7, 0.7, 0.7, 1)
#
#         # elif isinstance(socket, NodeSocketInt) or isinstance(socket, CCNCustomIntegerSocket):
#         #     return int(val) if val is not None else 0
#
#     return val  # Return for other socket types


class ObmSoundTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'ObmSoundTreeType'
    bl_label = "OnlyBlends Sound Editor"
    bl_icon = 'SOUND'
    bl_use_group_interface = True
    color_tag = 'COLOR'


class WavImportSocket(NodeSocket):
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


class NodeTreeInterfaceSocketWavImport(NodeTreeInterfaceSocket):
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


class ImportWavNode(ObmSoundNode, NodeCustomGroup):
    bl_idname = 'ImportWavNodeType'
    bl_label = "Import WAV"
    import_path: bpy.props.StringProperty(update=lambda self, context: self.__update_import_path())
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.create_import_wave_panel(self, uuid_tmp)
        self.inputs.new("WavImportSocketType", "Wave File")
        self.outputs.new('SoundSocketType', "Sound")
        # self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

    def free(self):
        if self.node_uuid in Data.uuid_operator_class_storage:
            bpy.utils.unregister_class(Data.uuid_operator_class_storage[self.node_uuid])

    def __update_import_path(self):
        print("__update_import_path")
        self.inputs[0].input_value = self.import_path
        args = {"filepath": self.import_path}

        # sound datablock which can also be used with speaker
        result = bpy.ops.sound.open(**args)

        # from pathlib import Path
        # file_name = Path(self.filepath).name
        # print(file_name)
        last = None
        sound = None
        for s in bpy.data.sounds:
            if s.filepath == self.import_path:
                last = s
                sound = bpy.types.BlendDataSounds(last)
        self.outputs[0].input_value = sound
        print(sound)
        device = aud.Device()
        aud_sound = aud.Sound.file(self.import_path)
        handle2 = device.play(aud_sound)


class SoundInfoNode(ObmSoundNode, NodeCustomGroup):
    '''Sound from an object'''

    bl_idname = 'SoundInfoNodeType'
    bl_label = "Sound Info"

    def init(self, context):
        self.inputs.new('SoundSocketType', "Sound")
        self.outputs.new('NodeSocketString', "Path")
        self.outputs.new('NodeSocketString', "Blender Path")
        self.outputs.new('NodeSocketString', "Channels")
        self.outputs.new('NodeSocketInt', "Samplerate")
        # self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Infos")
        # r = layout.row()
        # r.prop(self, 'import_path', text="")
        layout.label(text="Path: " + self.outputs[0].default_value)
        layout.label(text="Blender Path: " + self.outputs[1].default_value)
        layout.label(text="Channels: " + self.outputs[2].default_value)
        layout.label(text="Samplerate: " + str(self.outputs[3].default_value))
        # r.label(text="Path: " + self.outputs[0].default_value)

    def refresh_outputs(self):
        self.outputs[0].default_value = self.inputs[0].input_value.filepath
        self.outputs[1].default_value = self.inputs[0].input_value.name_full
        self.outputs[2].default_value = self.inputs[0].input_value.channels
        self.outputs[3].default_value = self.inputs[0].input_value.samplerate

    def draw_label(self):
        return "Sound Info"

    def insert_link(self, link):
        print("link")
        print(link)
        s = link.from_socket.input_value
        self.inputs[0].input_value = link.from_socket.input_value
        self.refresh_outputs()

    def update(self):
        # This method is called when the node updates
        print("update Sound Info")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        if isinstance(socket, SoundSocket):
            print("Sound Socket")
            if not self.inputs[0].is_linked:
                if self.inputs[0].input_value is not None:
                    self.refresh_outputs()

    def get_geometry(self):
        object_ = self.inputs[0].default_value
        if object_ is not None:
            depsgraph = bpy.context.view_layer.depsgraph
            obj_eval = depsgraph.id_eval_get(object_)
            geometry = obj_eval.evaluated_geometry()
            # pc = geometry.pointcloud
            return geometry
        else:
            return None


class SoundSampleSocket(NodeSocket):
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

    @classmethod
    def draw_color_simple(cls):
        # cls.display_shape = "SQUARE"
        return COLOR_SOUND_SAMPLE_SOCKET


class NodeTreeInterfaceSocketSoundSample(NodeTreeInterfaceSocket):
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


class DeviceSocket(NodeSocket):
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


class NodeTreeInterfaceSocketDevice(NodeTreeInterfaceSocket):
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


class SoundToSampleNode(ObmSoundNode, NodeCustomGroup):
    '''Sound Sample  which can be modified, played and recorded'''

    bl_idname = 'SoundToSampleNodeType'
    bl_label = "Sound To Sample"
    # update=lambda self, context: self.update_sound_prop(),
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.inputs.new('SoundSocketType', "Sound")
        self.outputs.new('SoundSampleSocketType', "Sound Sample")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Infos")
        layout.label(text=self.outputs[0].input_value)
        if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
            layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            # r = layout.row()
            # r.prop(self, 'import_path', text="")
            # layout.label(text="Path: " + self.outputs[0].default_value)
            # layout.label(text="Blender Path: " + self.outputs[1].default_value)
            # layout.label(text="Channels: " + self.outputs[2].default_value)
            # layout.label(text="Samplerate: " + str(self.outputs[3].default_value))
            # r.label(text="Path: " + self.outputs[0].default_value)

    def refresh_outputs(self):
        print("refresh outputs")
        if self.inputs[0].input_value is not None:
            Data.uuid_data_storage[self.node_uuid] = aud.Sound.file(self.inputs[0].input_value.filepath)
            self.outputs[0].input_value = self.node_uuid

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        print(link)
        s = link.from_socket.input_value
        # insert into logic
        if isinstance(link.from_socket, SoundSocket):
            self.inputs[0].input_value = link.from_socket.input_value
            self.refresh_outputs()
        else:
            print("männlich")

    def update(self):
        # This method is called when the node updates
        print("update Sound Info")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        if isinstance(socket, SoundSocket):
            print("Sound Socket")
            if not self.inputs[0].is_linked:
                if self.inputs[0].input_value is None:
                    Data.uuid_data_storage[self.node_uuid] = None
                else:
                    self.refresh_outputs()


class EditSampleNode(ObmSoundNode, NodeCustomGroup):
    '''Sound Sample  which can be modified, played and recorded'''

    bl_idname = 'CutSampleNodeType'
    bl_label = "Edit Sample"
    node_uuid: bpy.props.StringProperty()
    operations = [
        ('JOIN', "Join", "Plays two Samples in sequence"),
        ('MIX', "Mix", "Mixes two Samples"),
        ('MODULATE', "Modulate", "Modulates two Samples"),
        ('DELAY', "Delay", "Adds delay to Sample"),
        ('ENVELOPE', "Envelope", "Adds a more complex delay to Sample. Synth Buttons"),
        ('FADEIN', "Fadein", "Fades a Sample in by raising the volume linearly in the given time interval"),
        ('FADEOUT', "Fadeout", "Fades a Sample in by lowering the volume linearly in the given time interval."),
        ('ADSR', 'ADSR',
         "Attack-Decay-Sustain-Release envelopes the volume of a sound. Note: there is currently no way to trigger the release with this API."),
        ('LIMIT', "Limit", "Limits a sample within a specific start and end time."),
        ('LOOP', "Loop", "Loops a Sample"),
        ('HIGHPASS', "Highpass", "Creates a second order highpass filter based on the transfer function"),
        ('LOWPASS', "Lowpass", "Creates a second order lowpass filter based on the transfer function"),

    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='LIMIT'
        , update=lambda self, context: self.operation_update())

    def init(self, context):
        # self.use_custom_color = True
        # self.color = (0.2, 0.0, 0.2)
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        # self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.outputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs.new("FloatSocketType", "start")
        self.inputs.new("FloatSocketType", "end")

        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        self.outputs[0].input_value = self.node_uuid

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        print("Copying from node ", node)
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.uuid_data_storage[self.node_uuid] = Data.uuid_data_storage[node.node_uuid]
        self.outputs[0].input_value = self.node_uuid

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.inputs[0].input_value)
            layout.label(text=self.outputs[0].input_value)
        layout.prop(self, "operation", text="Operation")

    def operation_update(self):
        length_inputs = len(self.inputs)
        list_of_inputs = []
        for i in range(1, length_inputs):
            list_of_inputs.append(self.inputs[i])
        for socket in list_of_inputs:
            self.inputs.remove(socket)
        if self.operation == 'DELAY':
            self.inputs.new("FloatSocketType", "time")
        elif self.operation == 'JOIN':
            self.inputs.new('SoundSampleSocketType', "Sound Sample")
            self.inputs[1].display_shape = SOUND_SOCKET_SHAPE
        elif self.operation == 'MIX':
            self.inputs.new('SoundSampleSocketType', "Sound Sample")
            self.inputs[1].display_shape = SOUND_SOCKET_SHAPE
        elif self.operation == 'MODULATE':
            self.inputs.new('SoundSampleSocketType', "Sound Sample")
            self.inputs[1].display_shape = SOUND_SOCKET_SHAPE
        elif self.operation == 'ENVELOPE':
            self.inputs.new("FloatSocketType", "attack")
            self.inputs.new("FloatSocketType", "release")
            self.inputs.new("FloatSocketType", "threshold")
            self.inputs.new("FloatSocketType", "arthreshold")
        elif self.operation == 'FADEIN':
            self.inputs.new("FloatSocketType", "start")
            self.inputs.new("FloatSocketType", "length")
        elif self.operation == 'FADEOUT':
            self.inputs.new("FloatSocketType", "start")
            self.inputs.new("FloatSocketType", "length")
        elif self.operation == 'ADSR':
            self.inputs.new("FloatSocketType", "attack")
            self.inputs.new("FloatSocketType", "decay")
            self.inputs.new("FloatSocketType", "sustain")
            self.inputs.new("FloatSocketType", "release")
        elif self.operation == 'LIMIT':
            self.inputs.new("FloatSocketType", "start")
            self.inputs.new("FloatSocketType", "end")
        elif self.operation == 'LOOP':
            self.inputs.new("IntSocketType", "count")
        elif self.operation == "HIGHPASS":
            self.inputs.new("FloatSocketType", "frequency")
            self.inputs.new("FloatSocketType", "q")
        elif self.operation == "LOWPASS":
            self.inputs.new("FloatSocketType", "frequency")
            self.inputs.new("FloatSocketType", "q")

    def test_update(self, context):
        print("DELAY time")
        self.refresh_outputs()

    def refresh_outputs(self):
        print("refresh outputs")
        if self.inputs[0].input_value is not None and self.inputs[0].input_value != "":
            parent_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            new_sample = None
            if self.operation == 'DELAY':
                new_sample = parent_sample.delay(self.inputs[1].input_value)
            elif self.operation == 'JOIN':
                new_sample = parent_sample.join(Data.uuid_data_storage[self.inputs[1].input_value])
            elif self.operation == 'MIX':
                new_sample = parent_sample.mix(Data.uuid_data_storage[self.inputs[1].input_value])
            elif self.operation == 'MODULATE':
                new_sample = parent_sample.modulate(Data.uuid_data_storage[self.inputs[1].input_value])
            elif self.operation == 'ENVELOPE':
                new_sample = parent_sample.envelope(self.inputs[1].input_value, self.inputs[2].input_value,
                                                    self.inputs[3].input_value, self.inputs[4].input_value)
            elif self.operation == 'FADEIN':
                new_sample = parent_sample.fadein(self.inputs[1].input_value, self.inputs[2].input_value)
            elif self.operation == 'FADEOUT':
                new_sample = parent_sample.fadeout(self.inputs[1].input_value, self.inputs[2].input_value)
            elif self.operation == 'ADSR':
                new_sample = parent_sample.ADSR(self.inputs[1].input_value, self.inputs[2].input_value,
                                                self.inputs[3].input_value, self.inputs[4].input_value)
            elif self.operation == 'LIMIT':
                new_sample = parent_sample.limit(self.inputs[1].input_value, self.inputs[2].input_value)
            elif self.operation == 'LOOP':
                new_sample = parent_sample.loop(self.inputs[1].input_value)
            elif self.operation == 'HIGHPASS':
                new_sample = parent_sample.highpass(self.inputs[1].input_value, self.inputs[2].input_value)
            elif self.operation == 'LOWPASS':
                new_sample = parent_sample.lowpass(self.inputs[1].input_value, self.inputs[2].input_value)

            Data.uuid_data_storage[self.node_uuid] = new_sample
            # device = aud.Device()
            # device.play(new_sample)

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link edit sample node")
        if link.to_socket == self.inputs[0]:
            print("INPUT SAMPLE")
            self.inputs[0].input_value = link.from_socket.input_value
            self.refresh_outputs()
        elif link.to_socket == self.outputs[0]:
            print("OUTPUT SAMPLE")
        else:
            print("PARAMETER INPUT")
            link.to_socket.input_value = link.from_socket.input_value
            print("PARAMETER:", str(link.to_socket.input_value))
            if self.inputs[0].is_linked:
                self.refresh_outputs()
        # if link.to_node.name is self.name:
        #     print("im the target node")
        #     if link.to_socket is self.inputs[0]:
        #         print("update input Sample Socket of edit node")
        #         self.inputs[0].input_value = link.from_socket.input_value
        #     else:
        #         for sock in self.inputs:
        #             if sock is link.to_socket:
        #                 sock.input_value = link.from_socket.input_value
        #                 print("update input Parameter of edit node")
        # else:
        #     print("im the source node")

    def update(self):
        # This method is called when the node updates
        print("update edit sample node")
        self.refresh_outputs()

    def update_obm(self):
        self.update()
        for link in self.outputs[0].links:
            # link.to_node.update_obm(self, self.outputs[0])
            link.to_node.update_obm()

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        if isinstance(socket, SoundSampleSocket):
            print("Soubd Sample Socket update")
            for link in socket.links:
                print(link)
        elif not socket.is_output:
            print("pups")
            self.refresh_outputs()
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()


class OscillatorNode(ObmSoundNode, NodeCustomGroup):
    '''Sound Sample  which can be modified, played and recorded'''

    bl_idname = 'OscillatorNodeType'
    bl_label = "Oscillator"
    node_uuid: bpy.props.StringProperty()
    operations = [
        ('SAWTOOTH', "sawtooth", "Creates a sawtooth sound which plays a sawtooth wave."),
        ('SILENCE', "silence", "Creates a silence sound which plays simple silence."),
        ('SINE', "sine", "Creates a sine sound which plays a sine wave."),
        ('SQUARE', "square", "Creates a square sound which plays a square wave."),
        ('TRIANGLE', "triangle", "Creates a triangle sound which plays a triangle wave."),
    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='SILENCE'
        , update=lambda self, context: self.operation_update())

    def init(self, context):
        # self.use_custom_color = True
        # self.color = (0.2, 0.0, 0.2)
        self.outputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs.new("IntSocketType", "rate")
        self.inputs.new("FloatSocketType", "frequency")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

        self.outputs[0].input_value = self.node_uuid
        # Data.uuid_data_storage[self.node_uuid] =  aud.Sound.sine(44100)
        Data.uuid_data_storage[self.node_uuid] = aud.Sound.silence(44100).limit(0, 0.2)

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.uuid_data_storage[self.node_uuid] = Data.uuid_data_storage[node.node_uuid]
        self.outputs[0].input_value = self.node_uuid

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.outputs[0].input_value)
        layout.prop(self, "operation", text="Operation")

    def operation_update(self):
        length_inputs = len(self.inputs)
        list_of_inputs = []
        for i in range(0, length_inputs):
            list_of_inputs.append(self.inputs[i])
        for socket in list_of_inputs:
            self.inputs.remove(socket)
        if self.operation == "SINE":
            self.inputs.new("IntSocketType", "rate")
            self.inputs.new("FloatSocketType", "frequency")
        elif self.operation == "SQUARE":
            self.inputs.new("IntSocketType", "rate")
            self.inputs.new("FloatSocketType", "frequency")
        elif self.operation == "TRIANGLE":
            self.inputs.new("IntSocketType", "rate")
            self.inputs.new("FloatSocketType", "frequency")
        elif self.operation == "SAWTOOTH":
            self.inputs.new("IntSocketType", "rate")
            self.inputs.new("FloatSocketType", "frequency")
        elif self.operation == "SILENCE":
            self.inputs.new("IntSocketType", "rate")

    def test_update(self, context):
        print("DELAY time")
        self.refresh_outputs()

    def refresh_outputs(self):
        print("refresh outputs")
        if len(self.inputs) > 0 and len(self.outputs) > 0:
            new_sample = None
            if self.operation == "SINE":
                new_sample = aud.Sound.sine(self.inputs[1].input_value, self.inputs[0].input_value)
            elif self.operation == "SQUARE":
                new_sample = aud.Sound.square(self.inputs[1].input_value, self.inputs[0].input_value)
            elif self.operation == "TRIANGLE":
                new_sample = aud.Sound.triangle(self.inputs[1].input_value, self.inputs[0].input_value)
            elif self.operation == "SAWTOOTH":
                new_sample = aud.Sound.sawtooth(self.inputs[1].input_value, self.inputs[0].input_value)
            elif self.operation == "SILENCE":
                new_sample = aud.Sound.silence(self.inputs[0].input_value)
            Data.uuid_data_storage[self.node_uuid] = new_sample

        # device = aud.Device()
        # device.play(new_sample)

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("insert_link Oscillator Node")
        print(link)
        # s = link.from_socket.input_value
        # link.to_socket.input_value = link.from_socket.input_value
        for sock in self.inputs:
            if sock.identifier == link.to_socket.identifier:
                sock.input_value = link.from_socket.input_value
        print("after update")
        self.refresh_outputs()

    def update(self):
        # This method is called when the node updates
        print("update Oscilor Node")
        self.refresh_outputs()

    def update_obm(self):
        self.update()
        for link in self.outputs[0].links:
            # link.to_node.update_obm(self, self.outputs[0])
            link.to_node.update_obm()

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update Oscilor Node")
        if not socket.is_output:
            print("pups")
            self.refresh_outputs()
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()

    def socket_value_update(self, context):
        print("#######socket_value_update origin Oscilor Node")


class CreateDeviceNode(ObmSoundNode, NodeCustomGroup):
    '''A Device To Play Sound Samples'''

    bl_idname = 'CreateDeviceNodeType'
    bl_label = "Create Sound Device"
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.outputs.new('DeviceSocketType', "Device")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs.new('FloatSocketType', 'Volume')
        self.inputs[0].input_value = 1.0
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        self.create_device()
        self.outputs[0].input_value = uuid_tmp

    def create_device(self):
        device = aud.Device()
        device.volume = self.inputs[0].input_value
        Data.uuid_data_storage[self.node_uuid] = device

    def refresh_outputs(self):
        if self.node_uuid is not None and self.node_uuid != "":
            if self.node_uuid not in Data.uuid_data_storage:
                self.create_device()

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage.keys():
                layout.label(text="Volume: " + str(Data.uuid_data_storage[self.node_uuid].volume))

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        link.to_socket.input_value = link.from_socket.input_value
        self.create_device()

    def update(self):
        # This method is called when the node updates
        print("update Device Node")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        self.create_device()


class PlayDeviceNode(ObmSoundNode, NodeCustomGroup):
    '''A Device To Play Sound Samples'''

    bl_idname = 'PlayDeviceNodeType'
    bl_label = "Play Device"
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.inputs.new('DeviceSocketType', "Device")
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs[0].display_shape = DEVICE_SOCKET_SHAPE
        self.inputs[1].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        dummy = bpy.context.scene.samples.add()
        dummy.node_uuid = uuid_tmp
        self.node_uuid = dummy.node_uuid
        dummy.is_played = False

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        prop = self.get_ext_prop()
        bpy.context.scene.samples.remove(prop)
        for sample in bpy.context.scene.samples:
            print(sample)

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.inputs[1].input_value is None:
                layout.label(text="Duration: " + str(self.inputs[1].input_value.length))
        layout.prop(self.get_ext_prop(), 'is_played')

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        link.to_socket.input_value = link.from_socket.input_value
        prop = self.get_ext_prop()
        prop.sample_uuid = self.inputs[1].input_value
        prop.device_uuid = self.inputs[0].input_value

    def update(self):
        # This method is called when the node updates
        print("update Play Device Node")

    def update_obm(self):
        print("update obm Play Device Node")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)

    def get_ext_prop(self):
        final_prop = None
        for prop in bpy.context.scene.samples:
            if prop.node_uuid == self.node_uuid:
                final_prop = prop
                return final_prop
        return final_prop


class EditDeviceNode(ObmSoundNode, NodeCustomGroup):
    '''A Device To Play Sound Samples'''

    bl_idname = 'EditDeviceNodeType'
    bl_label = "Edit Sound Device"
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.outputs.new('DeviceSocketType', "Device")
        self.inputs.new('DeviceSocketType', "Device")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs.new('FloatSocketType', 'Volume')
        self.inputs[0].input_value = 1.0
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.uuid_data_storage[self.node_uuid] = aud.Device()
        Data.uuid_data_storage[self.node_uuid].volume = 1.0
        self.outputs[0].input_value = uuid_tmp

    def create_device(self):
        device = aud.Device()
        device.volume = self.inputs[0].input_value
        Data.uuid_data_storage[self.node_uuid] = device

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Debug Infos:")
        if self.node_uuid in Data.uuid_data_storage.keys():
            layout.label(text="Volume: " + str(Data.uuid_data_storage[self.node_uuid].volume))

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        link.to_socket.input_value = link.from_socket.input_value
        self.create_device()

    def update(self):
        # This method is called when the node updates
        print("update Device Node")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        self.create_device()


class CUSTOM_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "obm.socket_action"
    bl_label = "Socket Actions"
    bl_description = "Edit Socket of Gateway"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", "")))

    selection: bpy.props.IntProperty()

    node_name: bpy.props.StringProperty()

    def get_selected_node(self):
        for group in bpy.data.node_groups:
            for node in group.nodes:
                if self.node_name == node.name:
                    return node
        return None

    def invoke(self, context, event):
        scn = context.scene

        item = None
        idx = 0

        if self.action == 'DOWN' and idx < len(scn.custom) - 1:
            item_next = scn.custom[idx + 1].name
            scn.custom.move(idx, idx + 1)
            scn.custom_index += 1
            info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
            self.report({'INFO'}, info)

        elif self.action == 'UP' and idx >= 1:
            item_prev = scn.custom[idx - 1].name
            scn.custom.move(idx, idx - 1)
            scn.custom_index -= 1
            info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
            self.report({'INFO'}, info)

        elif self.action == 'REMOVE':
            node = self.get_selected_node()

            if self.selection == 0 or self.selection == (len(node.inputs) - 1):
                info = "First and Last Socket can't be removed"
            else:
                info = "Remove Socket Number " + str(self.selection)
                node.inputs.remove(node.inputs[self.selection])
            self.report({'INFO'}, info)

        return {"FINISHED"}


class CUSTOM_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.5)
        split.label(text="Index: %d" % (index))
        # custom_icon = "OUTLINER_OB_%s" % item.obj_type
        # split.prop(item, "name", text="", emboss=False, translate=False, icon=custom_icon)
        split.label(text=item.name)  # avoids renaming the item by accident

    def invoke(self, context, event):
        pass


class GatewayEntry(ObmSoundNode, Node):
    bl_idname = 'GatewayEntryNodeType'
    bl_label = "Gateway Entry"
    # node_uuid: bpy.props.StringProperty()
    show_options = True
    selection: bpy.props.IntProperty()
    remove_socket: bpy.props.BoolProperty(default=False)

    def init(self, context):
        self.inputs.new("StringSocketType", "Name")
        self.inputs[0].input_value = self.name
        self.inputs.new("EmptySocketType", "new socket")
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        selection = 0
        new_gateway = bpy.context.scene.obm_gateways.add()
        new_gateway.name = self.name
        new_gateway.socket_num = 0

    def draw_buttons(self, context, layout):
        # layout.label(text=self.get_node_tree_name())
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
        layout.label(text="selection: " + str(self.selection))

    def draw_buttons_ext(self, context, layout):
        scn = bpy.context.scene
        rows = 2
        row = layout.row()
        row.template_list("CUSTOM_UL_items", "", self, "inputs", self, "selection", rows=rows)
        col = row.column(align=True)
        # col.operator("obm.socket_action", icon='ADD', text="").action = 'ADD'

        op = col.operator("obm.socket_action", icon='REMOVE', text="")
        op.action = "REMOVE"
        op.selection = self.selection
        op.node_name = self.name
        col.separator()
        col.operator("obm.socket_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("obm.socket_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        # Data.uuid_data_storage[self.node_uuid] = Data.uuid_data_storage[node.node_uuid]
        # self.outputs[0].input_value = self.node_uuid

    def get_node_tree_name(self):
        for nodegroup in bpy.data.node_groups:
            for node in nodegroup.nodes:
                if node.name == self.name:
                    return nodegroup.name
        return None

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        # del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.

    def refresh_outputs(self):
        print("refresh outputs")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link gateway output node")
        if link.to_socket == self.inputs[-1]:
            print("INPUT SAMPLE")
            print(link.to_socket.type)
            t = link.from_socket.bl_idname

            to_connect = self.inputs.new(t, link.from_socket.name)

            tree_name = self.get_node_tree_name()
            new = self.inputs.new("EmptySocketType", "new input")
            tree = bpy.data.node_groups[tree_name]
            tree.links.new(link.from_socket, to_connect, handle_dynamic_sockets=True)
            # remove_socket = link.to_socket
            # self.inputs.remove(remove_socket)
            # HACK to avoid segmentation Error
            self.remove_socket = True
            return None

    def update(self):
        # This method is called when the node updates
        print("update gateoutput node")
        if self.remove_socket:
            self.remove_socket = False
            self.inputs.remove(self.inputs[-3])

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")


class GatewayExit(ObmSoundNode, Node):
    bl_idname = 'GatewayExitNodeType'
    bl_label = "Gateway Exit"

    # node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.inputs.new("StringSocketType", "Name")

    def draw_buttons(self, context, layout):
        # layout.label(text=self.get_node_tree_name())
        if IS_DEBUG:
            layout.label(text="Debug Infos:")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        # Data.uuid_data_storage[self.node_uuid] = Data.uuid_data_storage[node.node_uuid]
        # self.outputs[0].input_value = self.node_uuid

    def get_node_tree_name(self):
        for nodegroup in bpy.data.node_groups:
            for node in nodegroup.nodes:
                if node.name == self.name:
                    return nodegroup.name
        return None

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        # del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.

    def refresh_outputs(self):
        print("refresh outputs")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link gateway exit node")


    def update(self):
        # This method is called when the node updates
        print("update gateway exit node")


    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        if socket == self.inputs[0]:
            gateway_name = self.inputs[0].input_value
            for node_group in bpy.data.node_groups:
                for node in node_group.nodes:
                    if node.name == gateway_name:
                        print("node found")
                        print("node_type")
                        print(node.type)

                        for socket in node.inputs[1:-1]:
                            print(socket)
                            new_sock = self.outputs.new(socket.bl_idname, socket.name)
                            new_sock.input_value = socket.input_value
                            self.inputs.move(-1, 0)
# Add custom nodes to the Add menu.
def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != ObmSoundTree.bl_idname:
        # Avoid adding nodes to built-in node tree
        return
    # Add nodes to the layout. Can use submenus, separators, etc. as in any other menu.

    node_add_menu.add_node_type(layout, "ObmObjectNodeType")
    node_add_menu.add_node_type(layout, "ObmFloatNodeType")
    node_add_menu.add_node_type(layout, "ObmIntNodeType")
    node_add_menu.add_node_type(layout, "ObmStringNodeType")

    node_add_menu.add_node_type(layout, "SoundInfoNodeType")
    node_add_menu.add_node_type(layout, "ImportWavNodeType")

    node_add_menu.add_node_type(layout, "SoundToSampleNodeType")
    node_add_menu.add_node_type(layout, "CutSampleNodeType")

    node_add_menu.add_node_type(layout, "OscillatorNodeType")
    node_add_menu.add_node_type(layout, "PlayDeviceNodeType")
    node_add_menu.add_node_type(layout, "CreateDeviceNodeType")

    node_add_menu.add_node_type(layout, "GatewayEntryNodeType")
    node_add_menu.add_node_type(layout, "GatewayExitNodeType")
    # node_add_menu.draw_node_group_add_menu(context, layout)


classes = [
    ObjectNode,
    FloatNode,
    IntNode,
    StringNode,

    ObmSoundTree,
    SoundInfoNode,
    ImportWavNode, WavImportSocket, NodeTreeInterfaceSocketWavImport,
    SoundToSampleNode, SoundSampleSocket, NodeTreeInterfaceSocketSoundSample,
    EditSampleNode,
    OscillatorNode,
    PlayDeviceNode,
    CreateDeviceNode, DeviceSocket, NodeTreeInterfaceSocketDevice,

    GatewayEntry, GatewayExit,

    CUSTOM_UL_items, CUSTOM_OT_actions
]


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.NODE_MT_add.append(draw_add_menu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
