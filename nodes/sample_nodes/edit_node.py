import bpy
import aud

from ..basic_nodes import ObmSampleNode
from ...core.constants import SOUND_SOCKET_SHAPE, IS_DEBUG
from ...core.global_data import Data


class EditSampleNode(ObmSampleNode):
    '''Different functions to edit Samples. For example to limit the endless sample of an oscillator.'''
    bl_label = "Edit Sample"

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
        # ('RECHANNEL', "Rechannels", "Rechannels the sound."),
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
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new('SoundSampleSocketType', "Sample")
        float1_s = self.inputs.new("FloatSocketType", "Float")
        float2_s = self.inputs.new("FloatSocketType", "Float")
        self.inputs.new("FloatSocketType", "Float")
        self.inputs.new("FloatSocketType", "Float")
        self.inputs.new('BoolSocketType', "Additive")
        self.inputs.new("IntSocketType", "count")
        self.inputs.new('SoundSampleSocketType', "Sample")
        self.hide_all_socks()
        float1_s.hide = False
        float1_s.hide_value = False
        float2_s.hide = False
        float2_s.hide_value = False
        super().init(context)

    def hide_all_socks(self):
        for i, sock in enumerate(self.inputs):
            if i > 0:
                sock.hide = True
                sock.hide_value = True

    def operation_update(self):
        if self.inputs[0].input_value != "":
            parent_sample = Data.uuid_data_storage[self.inputs[0].input_value]
        else:
            parent_sample = None
        new_sample = None
        # sample_s = self.inputs[0]
        float1_s = self.inputs[1]
        float2_s = self.inputs[2]
        float3_s = self.inputs[3]
        float4_s = self.inputs[4]
        int_s = self.inputs[5]
        bool_s = self.inputs[6]
        sample2_s = self.inputs[7]
        self.hide_all_socks()
        if self.operation == 'DELAY':
            float1_s.hide = False
            float1_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.delay(float1_s.input_value).cache()
        elif self.operation == 'ACCUMULATE':
            bool_s.hide = False
            bool_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.accumulate(bool_s.input_value).cache()
        elif self.operation == 'JOIN':
            sample2_s.hide = False
            sample2_s.hide_value = False
            if parent_sample and sample2_s.is_linked and sample2_s.input_value and sample2_s.input_value != "":
                if sample2_s.input_value in Data.uuid_data_storage:
                    new_sample = parent_sample.join(Data.uuid_data_storage[sample2_s.input_value]).cache()

        elif self.operation == 'MIX':
            sample2_s.hide = False
            sample2_s.hide_value = False
            if parent_sample and sample2_s.is_linked and sample2_s.input_value and sample2_s.input_value != "":
                if sample2_s.input_value in Data.uuid_data_storage:
                    new_sample = parent_sample.mix(Data.uuid_data_storage[sample2_s.input_value]).cache()

        elif self.operation == 'MODULATE':
            sample2_s.hide = False
            sample2_s.hide_value = False
            if parent_sample and sample2_s.is_linked and sample2_s.input_value and sample2_s.input_value != "":
                if sample2_s.input_value in Data.uuid_data_storage:
                    new_sample = parent_sample.modulate(Data.uuid_data_storage[sample2_s.input_value]).cache()
        elif self.operation == 'ENVELOPE':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            float3_s.hide = False
            float3_s.hide_value = False
            float4_s.hide = False
            float4_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.envelope(float1_s.input_value, float2_s.input_value,
                                                    float3_s.input_value, float4_s.input_value).cache()

        elif self.operation == 'FADEIN':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            new_sample = parent_sample.fadein(float1_s.input_value, float2_s.input_value).cache()
        elif self.operation == 'FADEOUT':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            new_sample = parent_sample.fadeout(float1_s.input_value, float2_s.input_value).cache()
        elif self.operation == 'ADSR':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            float3_s.hide = False
            float3_s.hide_value = False
            float4_s.hide = False
            float4_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.ADSR(float1_s.input_value, float2_s.input_value,
                                                float3_s.input_value, float4_s.input_value).cache()
        elif self.operation == 'LIMIT':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.limit(float1_s.input_value, float2_s.input_value).cache()
        elif self.operation == 'LOOP':
            int_s.hide = False
            int_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.loop(int_s.input_value).cache()
        elif self.operation == 'HIGHPASS':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            float2_s.input_value = 0.5
            if parent_sample:
                new_sample = parent_sample.highpass(float1_s.input_value, float2_s.input_value).cache()
        elif self.operation == 'LOWPASS':
            float1_s.hide = False
            float1_s.hide_value = False
            float2_s.hide = False
            float2_s.hide_value = False
            float2_s.input_value = 0.5
            if parent_sample:
                new_sample = parent_sample.lowpass(float1_s.input_value, float2_s.input_value).cache()
        elif self.operation == 'PINGPONG':
            if parent_sample:
                new_sample = parent_sample.pingpong().cache()
        elif self.operation == 'REVERSE':
            if parent_sample:
                new_sample = parent_sample.reverse().cache()
        elif self.operation == 'PITCH':
            float1_s.hide = False
            float1_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.pitch(float1_s.input_value).cache()
        elif self.operation == 'SUM':
            if parent_sample:
                new_sample = parent_sample.sum().cache()

        elif self.operation == 'RESAMPLE':
            float1_s.hide = False
            float1_s.hide_value = False
            int_s.hide = False
            int_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.resample(float1_s.input_value, int_s.input_value).cache()
        elif self.operation == 'THRESHOLD':
            float1_s.hide = False
            float1_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.threshold(float1_s.input_value).cache()
        elif self.operation == 'VOLUME':
            float1_s.hide = False
            float1_s.hide_value = False
            if parent_sample:
                new_sample = parent_sample.volume(float1_s.input_value).cache()
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
        self.operation = node.operation
        for i, value in enumerate(node.inputs):
            self.inputs[i].input_value = node.inputs[i].input_value

    def socket_update(self, socket):
        if socket != self.outputs[0]:
            self.operation_update()
