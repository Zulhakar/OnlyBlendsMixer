import bpy
import aud

from ..basic_nodes import ObmSampleNode
from ...core.constants import SOUND_SOCKET_SHAPE, IS_DEBUG
from ...core.global_data import Data


class EditSampleNode(ObmSampleNode):
    '''Different functions to edit Samples. For example to limit the endless sample of an oscillator.'''
    bl_label = "Edit Sample"

    operations = [
        ('accumulate', "Accumulate", "Accumulates a sound by summing over positive input differences thus generating a"
                                     " monotonic sigal. If additivity is set to true negative input differences get"
                                     " added too, but positive ones with a factor of two. Note that with additivity"
                                     " the signal is not monotonic anymore."),

        ('join', "Join", "Plays two Samples in sequence"),
        ('mix', "Mix", "Mixes two Samples"),
        ('modulate', "Modulate", "Modulates two Samples"),
        ('delay', "Delay", "Adds delay to Sample"),
        ('envelope', "Envelope", "Adds a more complex delay to Sample. Synth Buttons"),
        ('fadein', "Fadein", "Fades a Sample in by raising the volume linearly in the given time interval"),
        ('fadeout', "Fadeout", "Fades a Sample in by lowering the volume linearly in the given time interval."),
        ('ADSR', "ADSR",
         "Attack-Decay-Sustain-Release envelopes the volume of a sound. Note: there is currently no way to trigger the release with this API."),
        ('limit', "Limit", "Limits a sample within a specific start and end time."),
        ('loop', "Loop", "Loops a Sample"),
        ('highpass', "Highpass", "Creates a second order highpass filter based on the transfer function"),
        ('lowpass', "Lowpass", "Creates a second order lowpass filter based on the transfer function"),

        ('pingpong', "Pingpong",
         "Plays a sound forward and then backward. This is like joining a sound with its reverse."),
        ('pitch', "Pitch", "Changes the pitch of a sound with a specific factor."),
        # ('RECHANNEL', "Rechannels", "Rechannels the sound."),
        ('resample', "Resample", "Resamples the sound."),
        ('reverse', "Reverse", "Plays a sound reversed"),
        ('sum', "Sum", "Sums the samples of a sound."),
        ('threshold', "Threshold",
         "Makes a threshold wave out of an audio wave by setting all samples with a amplitude >= threshold to 1, all <= -threshold to -1 and all between to 0."),
        ('volume', "Volume", "Changes the volume of a sound.")
    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='limit'
        , update=lambda self, context: self.operation_update())

    def init(self, context):
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new('SoundSampleSocketType', "Sample")
        float1_s = self.inputs.new("FloatSocketType", "Float")
        float2_s = self.inputs.new("FloatSocketType", "Float")
        self.inputs.new("FloatSocketType", "Float")
        self.inputs.new("FloatSocketType", "Float")
        self.inputs.new('BoolSocketType', "Additive")
        self.inputs.new("IntSocketType", "count")
        self.inputs.new('SoundSampleSocketType', "Sample")
        self.toggle_sockets(self.inputs[1:], True)
        self.toggle_sockets([float1_s, float2_s], False)
        super().init(context)

    def toggle_sockets(self, sockets, hide):
        for socket in sockets:
            socket.hide = hide
            socket.hide_value = hide

    def execute_sound_functions(self, parent_sample, function_name, sockets):
        self.toggle_sockets(sockets, False)
        if parent_sample:
            values = []
            sample_function = getattr(parent_sample, function_name)
            for socket in sockets:
                values.append(socket.input_value)
            return sample_function(*values).cache()
        else:
            return None

    def operation_update(self):
        if self.inputs[0].input_value != "":
            parent_sample = Data.uuid_data_storage[self.inputs[0].input_value]
        else:
            parent_sample = None
        sample_s = self.inputs[0]
        sample2_s = self.inputs[7]
        float1_s = self.inputs[1]
        float2_s = self.inputs[2]
        float3_s = self.inputs[3]
        float4_s = self.inputs[4]
        int_s = self.inputs[5]
        bool_s = self.inputs[6]
        self.toggle_sockets(self.inputs[1:], True)
        sockets = []
        if self.operation == 'accumulate':
            sockets = [bool_s]
        #        elif self.operation in ('pingpong', 'reverse', 'sum'):
        #            sockets = []
        elif self.operation in ('modulate', 'mix', 'join'):
            sockets = [sample2_s]
        elif self.operation == 'envelope' or self.operation == 'ADSR':
            sockets = [float1_s, float2_s, float3_s, float4_s]
        elif self.operation in ('fadein', 'fadeout', 'limit'):
            sockets = [float1_s, float2_s]
        elif self.operation == 'loop':
            sockets = [int_s]
        elif self.operation in ('highpass', 'lowpass'):
            #recursion
            #float2_s.input_value = 0.5
            sockets = [float1_s, float2_s]
        elif self.operation in ('pitch', 'volume', 'threshold', 'delay'):
            float1_s.bl_label = self.operation
            sockets = [float1_s]
        elif self.operation == 'resample':
            sockets = [float1_s, int_s]
        new_sample = self.execute_sound_functions(parent_sample, self.operation, sockets)
        if new_sample is None:
            Data.uuid_data_storage[self.node_uuid] = parent_sample
        else:
            Data.uuid_data_storage[self.node_uuid] = new_sample

        self.outputs[0].input_value = self.node_uuid
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.inputs[0].input_value)
            layout.label(text=self.outputs[0].input_value)
        layout.prop(self, "operation", text="Operation")

    def copy(self, node):
        super().copy(node)
        print("Copy")
        self.inputs[0].input_value = ""

    def socket_update(self, socket):
        if socket != self.outputs[0]:
            self.operation_update()
