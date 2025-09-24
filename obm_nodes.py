import bpy
import uuid
import aud
import numpy as np

from .constants import SAMPLE_TO_GEOMETRY_NODE_DESCRIPTION, SAMPLE_TO_MESH_NODE_DESCRIPTION
from .basic_nodes import ObmSoundNode
from .basic_sockets import SoundSocket, ObmStringSocket
from .constants import SOUND_SOCKET_SHAPE, IS_DEBUG, DEVICE_SOCKET_SHAPE
from .obm_sockets import SoundSampleSocket
from .global_data import Data
from .util import get_node_tree_name


class ImportWavNode(ObmSoundNode, bpy.types.NodeCustomGroup):
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


class SoundInfoNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Sound from an object'''

    bl_idname = 'SoundInfoNodeType'
    bl_label = "Sound Info"

    def init(self, context):
        self.inputs.new('SoundSocketType', "Sound")
        self.outputs.new('NodeSocketString', "Path")
        self.outputs.new('NodeSocketString', "Blender Path")
        self.outputs.new('NodeSocketString', "Channels")
        self.outputs.new('NodeSocketInt', "Sample Rate")
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


class SoundToSampleNode(ObmSoundNode, bpy.types.NodeCustomGroup):
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


class EditSampleNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Sound Sample  which can be modified, played and recorded'''
    bl_idname = 'CutSampleNodeType'
    bl_label = "Edit Sample"
    node_uuid: bpy.props.StringProperty()
    operations = [
        ('ACCUMULATE', "Accumulate", "Accumulates a sound by summing over positive input differences thus generating a"
                                     " monotonic sigal. If additivity is set to true negative input differences get"
                                     " added too, but positive ones with a factor of two. Note that with additivity"
                                     " the signal is not monotonic anymore."),

        ('JOIN', "Join", "Plays two Samples in sequence"),
        ('MIX', "Mix", "Mixes two Samples"),
        ('MODULATE', "Modulate", "Modulates two Samples"),
        ('DELAY', "Delay", "Adds delay to Sample"),
        ('ENVELOPE', "Envelope", "Adds a more complex delay to Sample. Synth Buttons"),
        ('FADEIN', "Fadein", "Fades a Sample in by raising the volume linearly in the given time interval"),
        ('FADEOUT', "Fadeout", "Fades a Sample in by lowering the volume linearly in the given time interval."),
        ('ADSR', "ADSR",
         "Attack-Decay-Sustain-Release envelopes the volume of a sound. Note: there is currently no way to trigger the release with this API."),
        ('LIMIT', "Limit", "Limits a sample within a specific start and end time."),
        ('LOOP', "Loop", "Loops a Sample"),
        ('HIGHPASS', "Highpass", "Creates a second order highpass filter based on the transfer function"),
        ('LOWPASS', "Lowpass", "Creates a second order lowpass filter based on the transfer function"),

        ('PINGPONG', "Pingpong",
         "Plays a sound forward and then backward. This is like joining a sound with its reverse."),
        ('PITCH', "Pitch", "Changes the pitch of a sound with a specific factor."),
        ('RECHANNEL', "Rechannels", "Rechannels the sound."),
        ('RESAMPLE', "Resample", "Resamples the sound."),
        ('REVERSE', "Reverse", "Plays a sound reversed"),
        ('SUM', "Sum", "Sums the samples of a sound."),
        ('THRESHOLD', "Threshold",
         "Makes a threshold wave out of an audio wave by setting all samples with a amplitude >= threshold to 1, all <= -threshold to -1 and all between to 0."),
        ('VOLUME', "Volume", "Changes the volume of a sound.")
    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='LIMIT'
        , update=lambda self, context: self.operation_update())

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.outputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs.new("FloatSocketType", "start")
        self.inputs.new("FloatSocketType", "end")

        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        # self.outputs[0].input_value = self.node_uuid

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        super().copy(node)
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        self.outputs[0].input_value = ""

    # Free function to clean up on removal.
    def free(self):
        super().free()
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
        elif self.operation == 'ACCUMULATE':
            self.inputs.new('BoolSocketType', "Additive")
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
        elif self.operation == 'HIGHPASS':
            self.inputs.new("FloatSocketType", "frequency")
            self.inputs.new("FloatSocketType", "q")
        elif self.operation == 'LOWPASS':
            self.inputs.new("FloatSocketType", "frequency")
            self.inputs.new("FloatSocketType", "q")
        elif self.operation == 'PINGPONG':
            pass
        elif self.operation == 'REVERSE':
            pass
        elif self.operation == 'PITCH':
            self.inputs.new("FloatSocketType", "factor")
        elif self.operation == 'SUM':
            pass
        elif self.operation == 'RECHANNEL':
            self.inputs.new("IntSocketType", "channels")
        elif self.operation == 'RESAMPLE':
            self.inputs.new("FloatSocketType", "rate")
            self.inputs.new("IntSocketType", "quality")
        elif self.operation == 'THRESHOLD':
            self.inputs.new("FloatSocketType", "threshold")
        elif self.operation == 'VOLUME':
            self.inputs.new("FloatSocketType", "volume")

    def test_update(self, context):

        self.refresh_outputs()

    def refresh_outputs(self):
        super().refresh_outputs()
        if self.inputs[0].input_value is not None and self.inputs[0].input_value != "":
            parent_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            new_sample = None
            if self.operation == 'DELAY':
                new_sample = parent_sample.delay(self.inputs[1].input_value)
            elif self.operation == 'ACCUMULATE':
                new_sample = parent_sample.accumulate(self.inputs[1].input_value)
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
            elif self.operation == 'PINGPONG':
                new_sample = parent_sample.pingpong()
            elif self.operation == 'REVERSE':
                new_sample = parent_sample.reverse()
            elif self.operation == 'PITCH':
                new_sample = parent_sample.pitch(self.inputs[1].input_value)
            elif self.operation == 'SUM':
                new_sample = parent_sample.sum()
            elif self.operation == 'RECHANNEL':
                new_sample = parent_sample.rechannel(self.inputs[1].input_value)
            elif self.operation == 'RESAMPLE':
                new_sample = parent_sample.resample(self.inputs[1].input_value, self.inputs[2].input_value)
            elif self.operation == 'THRESHOLD':
                new_sample = parent_sample.threshold(self.inputs[1].input_value)
            elif self.operation == 'VOLUME':
                new_sample = parent_sample.volume(self.inputs[1].input_value)
            Data.uuid_data_storage[self.node_uuid] = new_sample

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.bl_idname != link.from_socket.bl_idname:
            print("Wrong Socket Type")
        elif link.to_socket == self.inputs[0]:
            self.outputs[0].input_value = self.node_uuid
            self.inputs[0].input_value = link.from_socket.input_value
            self.refresh_outputs()
        else:
            link.to_socket.input_value = link.from_socket.input_value
            print("PARAMETER:", str(link.to_socket.input_value))
            if self.inputs[0].is_linked:
                self.refresh_outputs()

    def update(self):
        super().update()
        if not self.inputs[0].is_linked:
            self.inputs[0].input_value = ""
        self.refresh_outputs()

    def update_obm(self):
        self.update()
        for link in self.outputs[0].links:
            # link.to_node.update_obm(self, self.outputs[0])
            link.to_node.update_obm()

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            self.refresh_outputs()
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()


class OscillatorNode(ObmSoundNode, bpy.types.NodeCustomGroup):
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
        , default='SINE'
        , update=lambda self, context: self.operation_update())

    prev_frequency: bpy.props.FloatProperty(default=0.0)

    def init(self, context):

        self.outputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs.new("IntSocketType", "rate")
        self.inputs.new("FloatSocketType", "frequency")
        self.inputs[1].input_value = 110.0
        self.inputs[0].input_value = 44100
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

        self.outputs[0].input_value = self.node_uuid
        # Data.uuid_data_storage[self.node_uuid] =  aud.Sound.sine(44100)
        Data.uuid_data_storage[self.node_uuid] = aud.Sound.silence(44100).limit(0, 0.2)

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        super().copy(node)
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.uuid_data_storage[self.node_uuid] = Data.uuid_data_storage[node.node_uuid]
        self.outputs[0].input_value = self.node_uuid

    # Free function to clean up on removal.
    def free(self):
        super().free()
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
        if self.operation == "SILENCE":
            self.prev_frequency = self.inputs[1].input_value
            self.inputs.remove(self.inputs[1])
        else:
            if len(self.inputs) <= 1:
                self.inputs.new("FloatSocketType", "frequency")
                self.inputs[1].input_value = self.prev_frequency
        self.update()

    def refresh_outputs(self):
        super().refresh_outputs()
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

    def insert_link(self, link):
        super().insert_link(link)
        for sock in self.inputs:
            if sock.identifier == link.to_socket.identifier:
                sock.input_value = link.from_socket.input_value

        self.refresh_outputs()

    def update(self):
        # This method is called when the node updates
        super().update()
        self.refresh_outputs()

    def get_exit_nodes(self):
        exit_nodes = []
        for nodegroup in bpy.data.node_groups:
            for node in nodegroup.nodes:
                # if node.
                if node.name == self.name:
                    return nodegroup.name
        return None

    def update_obm(self):
        super().update_obm()
        self.update()
        for link in self.outputs[0].links:
            # link.to_node.update_obm(self, self.outputs[0])
            link.to_node.update_obm()

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            self.refresh_outputs()
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()


class CreateDeviceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
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


class PlayDeviceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''A Device To Play Sound Samples on specific frame. Animatable'''

    bl_idname = 'PlayDeviceNodeType'
    bl_label = "Play Device"

    def init(self, context):
        self.inputs.new('DeviceSocketType', "Device")
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs[0].display_shape = DEVICE_SOCKET_SHAPE
        self.inputs[1].display_shape = SOUND_SOCKET_SHAPE
        dummy = bpy.context.scene.samples.add()
        dummy.node_name = self.name
        dummy.is_played = False

    def free(self):
        super().free()
        prop = self.get_ext_prop()
        bpy.context.scene.samples.remove(prop)
        for sample in bpy.context.scene.samples:
            print(sample)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.inputs[1].input_value is None:
                layout.label(text="Duration: " + str(self.inputs[1].input_value.length))
        layout.prop(self.get_ext_prop(), 'is_played')

    def insert_link(self, link):
        super().insert_link(link)
        link.to_socket.input_value = link.from_socket.input_value
        prop = self.get_ext_prop()
        prop.sample_uuid = self.inputs[1].input_value
        prop.device_uuid = self.inputs[0].input_value

    def get_ext_prop(self):
        final_prop = None
        for prop in bpy.context.scene.samples:
            if prop.node_name == self.name:
                final_prop = prop
                return final_prop
        return final_prop


class PLAY_DEVICE_OT_actions(bpy.types.Operator):
    """Play Device"""
    bl_idname = "obm.device_action_op"
    bl_label = "Device Actions"
    bl_description = "Play Device"
    bl_options = {'REGISTER'}

    sample_uuid: bpy.props.StringProperty()

    device_uuid: bpy.props.StringProperty()

    action: bpy.props.StringProperty()

    def invoke(self, context, event):
        info = "test info"
        self.report({'INFO'}, info)
        sound = Data.uuid_data_storage[self.sample_uuid]
        device = Data.uuid_data_storage[self.device_uuid]
        if self.action == "PLAY":
            handle = device.play(sound)
        elif self.action == "STOP_ALL":
            handle = device.stopAll()
        return {"FINISHED"}


class PLAY_DEVICE_OT_actions2(bpy.types.Operator):
    """Play Device"""
    bl_idname = "obm.device_action2_op"
    bl_label = "Device Actions"
    bl_description = "Play Device"
    bl_options = {'REGISTER'}

    sample_uuid: bpy.props.StringProperty()

    device_uuid: bpy.props.StringProperty()

    action: bpy.props.StringProperty()

    handle: None

    def execute(self, context):
        print("execute")
        sound = Data.uuid_data_storage[self.sample_uuid]
        device = Data.uuid_data_storage[self.device_uuid]
        if self.action == "PLAY":
            self.handle = device.play(sound)
            return {'FINISHED'}
        elif self.action == "STOP_ALL":
            self.handle = device.stopAll()
            return {"FINISHED"}
        return {"FINISHED"}

    # def modal(self, context, event):
    #     if event.type != "TIMER_REPORT":
    #         print(event.type)
    #     if event.type == 'LEFTMOUSE':  # Confirm.
    #         print("finish")
    #         if event.value == "PRESS":
    #             sound = Data.uuid_data_storage[self.sample_uuid]
    #             device = Data.uuid_data_storage[self.device_uuid]
    #             handle = device.play(sound)
    #             print("PRESS")
    #         elif event.value == "RELEASE":
    #             print("RELEASE")
    #             device = Data.uuid_data_storage[self.device_uuid]
    #             device.stopAll()
    #         # return {'FINISHED'}
    #     elif event.type == "ESC":
    #         return {'FINISHED'}
    #     return {'RUNNING_MODAL'}

    # def invoke(self, context, event):
    #     print("INVOKE")
    #     print(event.type)
    #     info = "test info"
    #     self.report({'INFO'}, info)
    #     sound = Data.uuid_data_storage[self.sample_uuid]
    #     device = Data.uuid_data_storage[self.device_uuid]
    #     if self.action == "PLAY":
    #         # handle = device.play(sound)
    #         context.window_manager.modal_handler_add(self)
    #         return {'RUNNING_MODAL'}
    #     elif self.action == "STOP_ALL":
    #         handle = device.stopAll()
    #         return {"FINISHED"}


class DeviceActionNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''A Device To Play Sound Samples on specific frame. Animatable'''

    # operator siehe gateway entry
    bl_idname = 'DeviceActionNodeType'
    bl_label = "Device Actions"

    def init(self, context):
        self.inputs.new('DeviceSocketType', "Device")
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs[0].display_shape = DEVICE_SOCKET_SHAPE
        self.inputs[1].display_shape = SOUND_SOCKET_SHAPE

    def free(self):
        super().free()
        if self.inputs[0].input_value != "":
            device = Data.uuid_data_storage[self.device_uuid]
            device.stopAll()

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.inputs[1].input_value is None:
                layout.label(text="Duration: " + str(self.inputs[1].input_value.length))

        row = layout.row()
        op = row.operator("obm.device_action2_op", icon='PLAY', text="")
        op.device_uuid = self.inputs[0].input_value
        op.sample_uuid = self.inputs[1].input_value
        op.action = "PLAY"
        if hasattr(op, "handle"):
            if op.handle is not None:
                row.label(text=op.handle.status)
        op2 = row.operator("obm.device_action2_op", icon='KEY_EMPTY1_FILLED', text="")
        op2.device_uuid = self.inputs[0].input_value
        op2.sample_uuid = self.inputs[1].input_value
        op2.action = "STOP_ALL"

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.bl_idname != link.from_socket.bl_idname:
            print("error")
        else:
            link.to_socket.input_value = link.from_socket.input_value


class EditDeviceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
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
        super().copy(node)

    # Free function to clean up on removal.
    def free(self):
        super().free()
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Debug Infos:")
        if self.node_uuid in Data.uuid_data_storage.keys():
            layout.label(text="Volume: " + str(Data.uuid_data_storage[self.node_uuid].volume))

    def insert_link(self, link):
        super().insert_link(link)
        link.to_socket.input_value = link.from_socket.input_value
        self.create_device()

    def socket_update(self, socket):
        super().socket_update(socket)
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
        node = self.get_selected_node()
        if self.action == 'DOWN' and self.selection < len(node.inputs):
            if self.selection == 0:
                info = "Gateway Name Socket can't be moved"
                self.report({'INFO'}, info)
            elif self.selection == len(node.inputs) - 2:
                info = "Empty Socket have to be the last Socket"
                self.report({'INFO'}, info)
            else:
                node.inputs.move(self.selection, self.selection + 1)
                self.selection += 1
                node.selection += 1
                info = 'Item "%s" moved to position %d' % (node.name, self.selection)
                self.report({'INFO'}, info)

        elif self.action == 'UP' and self.selection >= 1:
            if self.selection == 1:
                info = "Gateway Name Socket must to be the first Socket"
                self.report({'INFO'}, info)
            elif self.selection == len(node.inputs) - 1:
                info = "Empty Socket can't be moved"
                self.report({'INFO'}, info)
            else:
                node.inputs.move(self.selection, self.selection - 1)
                self.selection -= 1
                node.selection -= 1
                info = 'Item "%s" moved to position %d' % (node.name, self.selection)
                self.report({'INFO'}, info)

        elif self.action == 'REMOVE':
            if self.selection == 0 or self.selection == (len(node.inputs) - 1):
                info = "First and Last Socket can't be removed"
            else:
                info = "Remove Socket Number " + str(self.selection)
                node.inputs.remove(node.inputs[self.selection])
            self.report({'INFO'}, info)

        return {"FINISHED"}


class CUSTOM_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # split = layout.split(factor=0.5)
        # split.label(text="Index: %d" % (index))
        # layout.label(text=item.name)  # avoids renaming the item by accident
        if index == 0:
            layout.label(text=item.name)
        elif index >= len(data.inputs) - 1:
            pass
        else:
            layout.prop(item, "name", emboss=False, text="")

    def invoke(self, context, event):
        pass




class GatewayEntry(ObmSoundNode, bpy.types.Node):
    bl_idname = 'GatewayEntryNodeType'
    bl_label = "Gateway Entry"
    show_options = True
    selection: bpy.props.IntProperty()
    remove_socket: bpy.props.BoolProperty(default=False)

    # added_sockets: bpy.props.CollectionProperty(type=GatewaySocketsCollection)

    def init(self, context):
        self.inputs.new("StringSocketType", "Name")
        self.inputs[0].input_value = self.name
        self.inputs.new("EmptySocketType", "Connect a link to create a new socket")
        new_gateway = bpy.context.scene.obm_gateways.add()
        new_gateway.name = self.name
        new_gateway.socket_num = 0

    def get_gateway_exits(self):
        exit_gateways = []
        for nodegroup in bpy.data.node_groups:
            for node in nodegroup.nodes:
                if node.bl_idname == 'GatewayExitNodeType':
                    if node.enum_gateways == self.name:
                        exit_gateways.append((node.name, nodegroup.name, node))
        return exit_gateways

    def draw_buttons(self, context, layout):

        if IS_DEBUG:
            layout.label(text="Debug Infos:")
        layout.label(text="selection: " + str(self.selection))

    def draw_buttons_ext(self, context, layout):
        scn = bpy.context.scene
        rows = 2
        row = layout.row()
        row.template_list("CUSTOM_UL_items", "", self, "inputs", self, "selection", rows=rows)
        col = row.column(align=True)

        op = col.operator("obm.socket_action", icon='REMOVE', text="")
        op.action = "REMOVE"
        op.selection = self.selection
        op.node_name = self.name
        col.separator()
        op2 = col.operator("obm.socket_action", icon='TRIA_UP', text="")
        op2.action = "UP"
        op2.selection = self.selection
        op2.node_name = self.name

        op3 = col.operator("obm.socket_action", icon='TRIA_DOWN', text="")
        op3.action = "DOWN"
        op3.selection = self.selection
        op3.node_name = self.name

        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket == self.inputs[-1]:
            t = link.from_socket.bl_idname

            to_connect = self.inputs.new(t, link.from_socket.name)
            if link.from_socket.bl_idname == "SoundSampleSocketType":
                to_connect.display_shape = SOUND_SOCKET_SHAPE
            elif link.from_socket.bl_idname == "DeviceSocketType":
                to_connect.display_shape = DEVICE_SOCKET_SHAPE
            tree_name = get_node_tree_name(self)
            new = self.inputs.new("EmptySocketType", "new input")
            tree = bpy.data.node_groups[tree_name]
            tree.links.new(link.from_socket, to_connect, handle_dynamic_sockets=True)
            # remove_socket = link.to_socket
            # self.inputs.remove(remove_socket)
            # HACK to avoid segmentation Error
            self.remove_socket = True
            allready_connected_g_exits = self.get_gateway_exits()
            if len(allready_connected_g_exits) > 0:
                for exit in allready_connected_g_exits:
                    name, node_tree, node = exit
                    exit_socket = node.outputs.new(t, link.from_socket.name)
                    exit_socket.display_shape = to_connect.display_shape
                    exit_socket.input_value = to_connect.input_value
            return None

    def update_obm(self):
        super().update_obm()
        exit_gateways = self.get_gateway_exits()
        for exit_gateway in exit_gateways:
            exit_gateway[2].refresh_outputs()

    def update(self):
        super().update()
        if self.remove_socket:
            self.remove_socket = False
            self.inputs.remove(self.inputs[-3])


def get_gateway_entries(self, context):
    existing_gateways = []
    for nodegroup in bpy.data.node_groups:
        for node in nodegroup.nodes:
            if node.bl_idname == 'GatewayEntryNodeType':
                existing_gateways.append((node.name, node.name, nodegroup.name))
    return existing_gateways


class GatewayExit(ObmSoundNode, bpy.types.Node):
    bl_idname = 'GatewayExitNodeType'
    bl_label = "Gateway Exit"

    enum_gateways: bpy.props.EnumProperty(name="enum_gateways", items=get_gateway_entries, description="",
                                          update=lambda self, context: self.update_gateways())

    def init(self, context):
        self.inputs.new("StringSocketType", "Name")

    def update_gateways(self):
        self.inputs[0].input_value = self.enum_gateways

    def draw_buttons(self, context, layout):
        # layout.label(text=self.get_node_tree_name())
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
        layout.prop(self, "enum_gateways")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        super().copy(node)
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
        super().free()

    def refresh_outputs(self):
        super().refresh_outputs()
        self.outputs.clear()
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
                        if new_sock.bl_idname == "SoundSampleSocketType" or new_sock.bl_idname == "DeviceSocketType":
                            new_sock.display_shape = SOUND_SOCKET_SHAPE
                        new_sock.input_value = socket.input_value
                        self.inputs.move(-1, 0)

    def insert_link(self, link):
        super().insert_link(link)

    def update(self):
        super().update()

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0]:
            self.refresh_outputs()


class GeometryToSampleNode(ObmSoundNode, bpy.types.Node):
    bl_idname = 'GeometryToSampleType'
    bl_label = "Geometry To Sample"

    node_uuid: bpy.props.StringProperty()

    operations = [
        ('POINTCLOUD', "Pointcloud", "Use Pointcloud from geometry to create Sound Sample"),
        ('MESH', "Mesh", "Use Mesh from geometry to create Sound Sample"),

    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='MESH'
        , update=lambda self, context: self.operation_update())

    def init(self, context):
        self.inputs.new("ObjectSocketType", "Object")
        self.inputs.new("StringSocketType", "Attribute")
        self.inputs.new("IntSocketType", "Axis")
        self.inputs[2].input_value = 1
        self.inputs.new("IntSocketType", "Sampling Rate")
        self.inputs[3].input_value = 44100
        self.outputs.new("SoundSampleSocketType", "Sound Sample")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        self.outputs[0].input_value = self.node_uuid
        Data.uuid_data_storage[self.node_uuid] = aud.Sound.silence(44100).limit(0, 0.2)
        Data.geometry_to_sample_nodes[self.node_uuid] = self


        bpy.context.scene.geometry_to_sample_nodes_num += 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 1:
            from .properties import on_depsgraph_update
            bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

    def operation_update(self):
        sound_sample = self.get_sound()
        Data.geometry_to_sample_nodes[self.node_uuid] = self
        Data.uuid_data_storage[self.node_uuid] = sound_sample

        for link in self.outputs[0].links:
            link.to_node.update_obm()

    def __depsgraph_to_sound(self, attribute, axis, obj, sampling_rate, option):
        depsgraph = bpy.context.view_layer.depsgraph
        track = []
        obj_eval = depsgraph.id_eval_get(obj)
        geometry = obj_eval.evaluated_geometry()
        domain_data = None
        if option == "POINTCLOUD":
            domain_data = geometry.pointcloud
        elif option == "MESH":
            domain_data = geometry.mesh
        attr_data = domain_data.attributes[attribute].data
        length_of_data = len(attr_data)
        duration = length_of_data / sampling_rate
        for vert in attr_data:
            v = vert.vector
            v_tup = tuple(v)
            track.append(v_tup[axis])
        sound_array = np.asarray([track]).T.astype(np.float32)
        sound_sample = aud.Sound.buffer(sound_array, sampling_rate)
        return sound_sample

    def get_sound(self):
        attribute = self.inputs[1].input_value
        option = self.operation
        obj = self.inputs[0].input_value
        sampling_rate = self.inputs[3].input_value
        axis = self.inputs[2].input_value
        return self.__depsgraph_to_sound(attribute, axis, obj, sampling_rate, option)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
        layout.prop(self, "operation", text="Operation")

    def free(self):
        super().free()
        bpy.context.scene.geometry_to_sample_nodes_num -= 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 0:
            from .properties import on_depsgraph_update
            bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)


def point_cloud_from_mesh_gn_node_group(name):
    point_cloud_from_mesh_gn = bpy.data.node_groups.new(type='GeometryNodeTree', name=name)

    point_cloud_from_mesh_gn.color_tag = 'NONE'
    point_cloud_from_mesh_gn.description = ""
    point_cloud_from_mesh_gn.default_group_node_width = 140

    point_cloud_from_mesh_gn.is_modifier = True

    # point_cloud_from_mesh_gn interface
    # Socket Geometry
    geometry_socket = point_cloud_from_mesh_gn.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                                    socket_type='NodeSocketGeometry')
    geometry_socket.attribute_domain = 'POINT'
    geometry_socket.default_input = 'VALUE'
    geometry_socket.structure_type = 'AUTO'

    # Socket Geometry
    geometry_socket_1 = point_cloud_from_mesh_gn.interface.new_socket(name="Geometry", in_out='INPUT',
                                                                      socket_type='NodeSocketGeometry')
    geometry_socket_1.attribute_domain = 'POINT'
    geometry_socket_1.default_input = 'VALUE'
    geometry_socket_1.structure_type = 'AUTO'

    # Socket Count
    count_socket = point_cloud_from_mesh_gn.interface.new_socket(name="Count", in_out='INPUT',
                                                                 socket_type='NodeSocketInt')
    count_socket.default_value = 10
    count_socket.min_value = 0
    count_socket.max_value = 2147483647
    count_socket.subtype = 'NONE'
    count_socket.attribute_domain = 'POINT'
    count_socket.description = "The number of points to create"
    count_socket.default_input = 'VALUE'
    count_socket.structure_type = 'AUTO'

    # initialize point_cloud_from_mesh_gn nodes
    # node Group Input
    group_input = point_cloud_from_mesh_gn.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"

    # node Group Output
    group_output = point_cloud_from_mesh_gn.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.is_active_output = True

    # node Points
    points = point_cloud_from_mesh_gn.nodes.new("GeometryNodePoints")
    points.name = "Points"
    # Radius
    points.inputs[2].default_value = 9.999999747378752e-06

    # node Position
    position = point_cloud_from_mesh_gn.nodes.new("GeometryNodeInputPosition")
    position.name = "Position"

    # node Sample Index
    sample_index = point_cloud_from_mesh_gn.nodes.new("GeometryNodeSampleIndex")
    sample_index.name = "Sample Index"
    sample_index.clamp = False
    sample_index.data_type = 'FLOAT_VECTOR'
    sample_index.domain = 'POINT'

    # node Index
    index = point_cloud_from_mesh_gn.nodes.new("GeometryNodeInputIndex")
    index.name = "Index"

    # node Domain Size
    domain_size = point_cloud_from_mesh_gn.nodes.new("GeometryNodeAttributeDomainSize")
    domain_size.name = "Domain Size"
    domain_size.component = 'MESH'

    # Set locations
    group_input.location = (-685.3740844726562, 166.578857421875)
    group_output.location = (156.9349822998047, 410.7016296386719)
    points.location = (-62.33095932006836, 563.706298828125)
    position.location = (-557.9932861328125, 430.3790588378906)
    sample_index.location = (-222.2251434326172, 328.3319396972656)
    index.location = (-651.409423828125, 356.1745300292969)
    domain_size.location = (-331.29730224609375, 631.0365600585938)

    # Set dimensions
    group_input.width, group_input.height = 140.0, 100.0
    group_output.width, group_output.height = 140.0, 100.0
    points.width, points.height = 140.0, 100.0
    position.width, position.height = 140.0, 100.0
    sample_index.width, sample_index.height = 140.0, 100.0
    index.width, index.height = 140.0, 100.0
    domain_size.width, domain_size.height = 140.0, 100.0

    # initialize point_cloud_from_mesh_gn links
    # points.Points -> group_output.Geometry
    point_cloud_from_mesh_gn.links.new(points.outputs[0], group_output.inputs[0])
    # group_input.Geometry -> sample_index.Geometry
    point_cloud_from_mesh_gn.links.new(group_input.outputs[0], sample_index.inputs[0])
    # position.Position -> sample_index.Value
    point_cloud_from_mesh_gn.links.new(position.outputs[0], sample_index.inputs[1])
    # sample_index.Value -> points.Position
    point_cloud_from_mesh_gn.links.new(sample_index.outputs[0], points.inputs[1])
    # index.Index -> sample_index.Index
    point_cloud_from_mesh_gn.links.new(index.outputs[0], sample_index.inputs[2])
    # domain_size.Point Count -> points.Count
    point_cloud_from_mesh_gn.links.new(domain_size.outputs[0], points.inputs[0])
    # group_input.Geometry -> domain_size.Geometry
    point_cloud_from_mesh_gn.links.new(group_input.outputs[0], domain_size.inputs[0])
    return point_cloud_from_mesh_gn


def point_cloud(ob_name, coords):
    """Create point cloud object based on given coordinates and name."""
    me = bpy.data.meshes.new(ob_name + "Mesh")
    ob = bpy.data.objects.new(ob_name, me)
    me.from_pydata(coords, [], [])
    # ob.show_name = True
    me.update()
    return ob


class SampleToGeometryNode(ObmSoundNode, bpy.types.Node):
    bl_idname = 'SampleToGeometryType'
    bl_label = "Sample To Geometry"

    def init(self, context):
        self.inputs.new("SoundSampleSocketType", "Sound Sample")
        self.inputs.new("StringSocketType", "Object Name")
        # self.inputs.new("IntSocketType", "Sampling Rate")
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE

    def create_geometry_node(self):
        channel_id = 0
        sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
        np_array_sound = sound_sample.data()
        file_name = self.inputs[2].input_value

        sample_rate, channels = sound_sample.specs
        duration = sound_sample.length / sample_rate

        # if channels < 2:
        #    np_array_sound = np.expand_dims(np_array_sound, axis=0)

        for channel in np_array_sound.T:
            # x = np.zeros(len(channel))
            x = np.linspace(0, duration, len(channel))
            # x = np.expand_dims(x, 0)
            # z = x.copy()
            z = np.zeros(len(channel))
            # z = np.expand_dims(z, 0)
            coord = np.vstack([x, channel, z])
            coord = coord.T
            coord = coord.tolist()
            object_name = f"{file_name}_channel_{channel_id}"
            new_pc = point_cloud(object_name, coord)
            node_group_name = file_name.split(".wav")[0] + "_pc_from_mesh_GN"
            bpy.context.collection.objects.link(new_pc)
            # geometry_nodes = point_cloud_from_mesh_gn_node_group(node_group_name)
            # new_pc.modifiers.new('GeometryNodes', 'NODES')
            # new_pc.modifiers['GeometryNodes'].node_group = bpy.data.node_groups[node_group_name]

            # new_pc.scale = (duration, 1, 1)

            channel_id += 1

    def draw_buttons(self, context, layout):
        # layout.label(text=self.get_node_tree_name())
        if IS_DEBUG:
            layout.label(text="Debug Infos:")

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.type != link.from_socket.type:
            print("Error")
            # TODO: handle wrong socket connection
            self.bl_icon = "NOT_FOUND"
            error_message = "Wrong Socket Connected " + link.from_socket.name
            self.bl_description = error_message

            def draw_error(self, context):
                self.layout.label(text=error_message)

            bpy.context.window_manager.popup_menu(draw_error, title="ERROR", icon="INFO")

            # tree_name = get_node_tree_name(self)
            # tree = bpy.data.node_groups[tree_name]
            # tree.links.remove(link)
        else:
            self.bl_icon = "NONE"
            self.bl_description = SAMPLE_TO_GEOMETRY_NODE_DESCRIPTION

        if self.inputs[1].input_value != "":
            self.create_geometry_node()

    def update(self):
        # This method is called when the node updates
        print("update Sample to Geometry")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update Sample to Geometry")


class SampleToMeshNode(ObmSoundNode, bpy.types.Node):
    '''Generate Mesh from Sound Sample'''
    bl_idname = 'SampleToMeshType'
    bl_label = "Sample To Mesh"

    def init(self, context):
        self.inputs.new("SoundSampleSocketType", "Sound Sample")
        self.inputs.new("StringSocketType", "Object Name")
        self.inputs.new("FloatSocketType", "Scale X")
        self.inputs.new("BoolSocketType", "Seperate channels?")
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs[2].input_value = 1.0
        self.inputs[3].input_value = True

    def __del_object_if_exit(self, object_name):
        if object_name in bpy.data.objects:
            obj = bpy.data.objects[object_name]
            bpy.data.objects.remove(obj, do_unlink=True)

    def __create_object(self):
        channel_id = 0
        sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
        file_name = self.inputs[1].input_value
        sample_rate, channels = sound_sample.specs
        print("channels")
        print(str(channels))
        for i in range(0, channels):
            object_name = f"{file_name}_channel_{i}"
            self.__del_object_if_exit(object_name)
        self.__del_object_if_exit(f"{file_name}")

        if not self.inputs[3].input_value:
            sound_sample = sound_sample.rechannel(1)
        np_array_sound = sound_sample.data()

        sample_rate, channels = sound_sample.specs
        duration = sound_sample.length / sample_rate
        scale = self.inputs[2].input_value

        for channel in np_array_sound.T:
            x = np.linspace(0, duration, len(channel))
            z = np.zeros(len(channel))
            coord = np.vstack([x, channel, z])
            coord = coord.T
            coord = coord.tolist()
            if self.inputs[3].input_value:
                object_name = f"{file_name}_channel_{channel_id}"
            else:
                object_name = f"{file_name}"

            new_pc = point_cloud(object_name, coord)
            bpy.context.collection.objects.link(new_pc)
            new_pc.scale = (duration * scale, 1, 1)
            channel_id += 1

    def update_obm(self):
        self.__create_object()

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.type != link.from_socket.type:
            print("Error")
            # TODO: handle wrong socket connection
            self.bl_icon = "NOT_FOUND"
            error_message = "Wrong Socket Connected " + link.from_socket.name
            self.bl_description = error_message

            def draw_error(self, context):
                self.layout.label(text=error_message)

            bpy.context.window_manager.popup_menu(draw_error, title="ERROR", icon="INFO")

        else:
            self.bl_icon = "NONE"
            self.bl_description = SAMPLE_TO_MESH_NODE_DESCRIPTION
            if link.from_socket.bl_idname == "SoundSampleSocketType":
                self.inputs[0].input_value = link.from_socket.input_value
                if self.inputs[0].input_value != "":
                    self.__create_object()

    def socket_update(self, socket):
        super().socket_update(socket)
        if self.inputs[0].input_value != "":
            self.update_obm()


class SampleToSoundNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Transform Sample to Sound'''

    bl_idname = 'SampleToSoundNodeType'
    bl_label = "Sample To Sound"
    # update=lambda self, context: self.update_sound_prop(),
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs.new("StringSocketType", "File Name")
        self.inputs.new("IntSocketType", "Sample Rate")
        self.inputs[2].input_value = 44100
        self.outputs.new('SoundSocketType', "Sound")
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

    def store_data(self):
        sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
        data_path = self.inputs[1].input_value
        sound_sample.write(data_path, self.inputs[2].input_value, 2)
        args = {"filepath": data_path}

        result = bpy.ops.sound.open(**args)

        last = None
        sound = None
        for s in bpy.data.sounds:
            if s.filepath == data_path:
                last = s
                sound = bpy.types.BlendDataSounds(last)
        self.outputs[0].input_value = sound

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

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        print(link)
        if isinstance(link.from_socket, ObmStringSocket):
            self.store_data()
        else:
            print("no update")

    def update(self):
        # This method is called when the node updates
        print("update Sample_to_sound node")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update sample_to_sound")
        print(socket)
        if isinstance(socket, ObmStringSocket):
            self.store_data()
        else:
            print("no update")


class SampleInfoNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Infos of Sound Sample'''
    bl_idname = 'SampleInfoNodeType'
    bl_label = "Sample Info"

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.outputs.new("IntSocketType", "Sample Num")
        self.outputs.new("FloatSocketType", "Duration")
        self.outputs.new("IntSocketType", "Sample Rate")
        self.outputs.new("IntSocketType", "Channels")
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Infos")
            if self.inputs[0].input_value is not None and self.inputs[0].input_value != "" and self.inputs[
                0].input_value in Data.uuid_data_storage and \
                    Data.uuid_data_storage[self.inputs[0].input_value] is not None:
                for output in (self.outputs[0], self.outputs[1], self.outputs[2], self.outputs[3]):
                    if output.name == "Duration":
                        layout.label(text=output.name + ": " + str(round(output.input_value, 4)))
                    else:
                        layout.label(text=output.name + ": " + str(output.input_value))

    def refresh_outputs(self):
        print("refresh outputs")
        if self.inputs[0].input_value != "":
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            self.outputs[0].input_value = sound_sample.length
            sample_rate, channels = sound_sample.specs
            self.outputs[2].input_value = int(sample_rate)
            self.outputs[3].input_value = channels
            if sound_sample.length == -1:
                self.outputs[0].input_value = -1
            else:
                if sample_rate != 0:
                    self.outputs[1].input_value = sound_sample.length / sample_rate
                else:
                    self.outputs[1].input_value = 0
                np_array = sound_sample.data()
                length2 = len(np_array)
                if length2 != sound_sample.length:
                    print("Not same length")
                    print(sound_sample.length)
                    print(length2)

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        print(link)
        if isinstance(link.from_socket, SoundSampleSocket):
            self.inputs[0].input_value = link.from_socket.input_value
            self.refresh_outputs()

    def update_obm(self):
        self.update()
        for output in (self.outputs[0], self.outputs[1], self.outputs[2], self.outputs[3]):
            for link in output.links:
                # link.to_node.update_obm(self, self.outputs[0])
                link.to_node.update_obm()

    def update(self):
        # This method is called when the node updates
        print("update Sample Info node")
        self.refresh_outputs()

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update Sound Info Node")
