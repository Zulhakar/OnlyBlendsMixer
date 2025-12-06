import bpy
import aud

from ..basic_nodes import ObmSampleNode
from ...core.constants import SOUND_SOCKET_SHAPE, IS_DEBUG
from ...core.global_data import Data


class EditSampleNode(ObmSampleNode):
    '''Sound Sample  which can be modified, played and recorded'''
    bl_idname = 'CutSampleNodeType'
    bl_label = "Edit Sample"

    # if node has node_uuid, an aud sound is stored, and free() and copy() are differ from the other nodes
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
        , update=lambda self, context: self.__operation_update())

    def __operation_update(self):
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
            q = self.inputs.new("FloatSocketType", "q")
            q.input_value = 0.5
        elif self.operation == 'LOWPASS':
            self.inputs.new("FloatSocketType", "frequency")
            q = self.inputs.new("FloatSocketType", "q")
            q.input_value = 0.5
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
        super().init(self)

    def __sound_function(self):
        if self.inputs[0].input_value != "" and self.inputs[0].input_value in Data.uuid_data_storage and Data.uuid_data_storage[self.inputs[0].input_value]:
            parent_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            length = parent_sample.length
            new_sample = None
            if self.operation == 'DELAY':
                new_sample = parent_sample.delay(self.inputs[1].input_value).cache()
            elif self.operation == 'ACCUMULATE':
                new_sample = parent_sample.accumulate(self.inputs[1].input_value).cache()
            elif self.operation == 'JOIN':
                if self.inputs[1].input_value != "" and self.inputs[1].input_value in Data.uuid_data_storage:
                    new_sample = parent_sample.join(Data.uuid_data_storage[self.inputs[1].input_value]).cache()
            elif self.operation == 'MIX':
                if self.inputs[1].input_value != "" and self.inputs[1].input_value in Data.uuid_data_storage:
                    new_sample = parent_sample.mix(Data.uuid_data_storage[self.inputs[1].input_value]).cache()
            elif self.operation == 'MODULATE':
                if self.inputs[1].input_value != "" and self.inputs[1].input_value in Data.uuid_data_storage:
                    new_sample = parent_sample.modulate(Data.uuid_data_storage[self.inputs[1].input_value]).cache()
            elif self.operation == 'ENVELOPE':
                if length > 0:
                    new_sample = parent_sample.envelope(self.inputs[1].input_value, self.inputs[2].input_value,
                                                    self.inputs[3].input_value, self.inputs[4].input_value).cache()
            elif self.operation == 'FADEIN':
                new_sample = parent_sample.fadein(self.inputs[1].input_value, self.inputs[2].input_value).cache()
            elif self.operation == 'FADEOUT':
                new_sample = parent_sample.fadeout(self.inputs[1].input_value, self.inputs[2].input_value).cache()
            elif self.operation == 'ADSR':
                new_sample = parent_sample.ADSR(self.inputs[1].input_value, self.inputs[2].input_value,
                                                self.inputs[3].input_value, self.inputs[4].input_value).cache()
            elif self.operation == 'LIMIT':
                new_sample = parent_sample.limit(self.inputs[1].input_value, self.inputs[2].input_value).cache()
            elif self.operation == 'LOOP':
                new_sample = parent_sample.loop(self.inputs[1].input_value).cache()
            elif self.operation == 'HIGHPASS':
                new_sample = parent_sample.highpass(self.inputs[1].input_value, self.inputs[2].input_value).cache()
            elif self.operation == 'LOWPASS':
                new_sample = parent_sample.lowpass(self.inputs[1].input_value, self.inputs[2].input_value).cache()
            elif self.operation == 'PINGPONG':
                new_sample = parent_sample.pingpong().cache()
            elif self.operation == 'REVERSE':
                new_sample = parent_sample.reverse().cache()
            elif self.operation == 'PITCH':
                new_sample = parent_sample.pitch(self.inputs[1].input_value).cache()
            elif self.operation == 'SUM':
                new_sample = parent_sample.sum().cache()
            elif self.operation == 'RECHANNEL':
                new_sample = parent_sample.rechannel(self.inputs[1].input_value).cache()
            elif self.operation == 'RESAMPLE':
                new_sample = parent_sample.resample(self.inputs[1].input_value, self.inputs[2].input_value).cache()
            elif self.operation == 'THRESHOLD':
                new_sample = parent_sample.threshold(self.inputs[1].input_value).cache()
            elif self.operation == 'VOLUME':
                new_sample = parent_sample.volume(self.inputs[1].input_value).cache()
            if new_sample is not None:
                Data.uuid_data_storage[self.node_uuid] = new_sample
                self.outputs[0].input_value = self.node_uuid
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
                    #if hasattr(link.to_node, "update_obm"):
                    #    link.to_node.update_obm()
            else:
                self.outputs[0].input_value = ""
                for link in self.outputs[0].links:
                    link.to_socket.input_value = ""
        else:
            if len(self.outputs) > 0:
                self.outputs[0].input_value = ""
                for link in self.outputs[0].links:
                    link.to_socket.input_value = ""

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sample")
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new("FloatSocketType", "start")
        self.inputs.new("FloatSocketType", "end")
        super().init(context)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.inputs[0].input_value)
            layout.label(text=self.outputs[0].input_value)
        layout.prop(self, "operation", text="Operation")

    def state_update(self):
        super().state_update()
        self.__sound_function()

    def copy(self, node):
        super().copy(node)
        print("Copy")
        self.operation = node.operation
        for i, value in enumerate(node.inputs):
            self.inputs[i].input_value = node.inputs[i].input_value
            #node.operation = self.operation
            #node.inputs[i].input_value = self.inputs[i].input_value