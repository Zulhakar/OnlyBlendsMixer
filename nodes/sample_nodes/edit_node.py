from pickletools import float8

import bpy
import aud

from ..basic_nodes import ObmSampleNode
from ...core.constants import SOUND_SOCKET_SHAPE, IS_DEBUG
from ...core.global_data import Data

class EditSampleNode(ObmSampleNode):
    '''Different functions to edit Samples. For example to limit the endless sample of an oscillator.'''
    bl_label = "Edit Sample"

    operations = [
        ('volume', "Volume", "Changes the volume of a sound."),
        ('pitch', "Pitch", "Changes the pitch of a sound with a specific factor."),
        # ('RECHANNEL', "Rechannels", "Rechannels the sound."),
        ('threshold', "Threshold",
         "Makes a threshold wave out of an audio wave by setting all samples with a amplitude >= threshold to 1, all <= -threshold to -1 and all between to 0."),
        (None),
        ('join', "Join", "Plays two Samples in sequence"),
        ('mix', "Mix", "Mixes two Samples"),
        ('modulate', "Modulate", "Modulates two Samples"),
        (None),
        ('delay', "Delay", "Adds delay to Sample"),
        ('fadein', "Fadein", "Fades a Sample in by raising the volume linearly in the given time interval"),
        ('fadeout', "Fadeout", "Fades a Sample in by lowering the volume linearly in the given time interval."),
        (None),
        ('ADSR', "ADSR",
         "Attack-Decay-Sustain-Release envelopes the volume of a sound. Note: there is currently no way to trigger the release with this API."),
        ('envelope', "Envelope", "Adds a more complex delay to Sample. Synth Buttons"),
        (None),
        ('accumulate', "Accumulate", "Accumulates a sound by summing over positive input differences thus generating a"
                                     " monotonic sigal. If additivity is set to true negative input differences get"
                                     " added too, but positive ones with a factor of two. Note that with additivity"
                                     " the signal is not monotonic anymore."),
        (None),
        ('highpass', "Highpass", "Creates a second order highpass filter based on the transfer function"),
        ('lowpass', "Lowpass", "Creates a second order lowpass filter based on the transfer function"),
        (None),
        ('limit', "Limit", "Limits a sample within a specific start and end time."),
        ('loop', "Loop", "Loops a Sample"),

        (None),
        ('pingpong', "Pingpong",
         "Plays a sound forward and then backward. This is like joining a sound with its reverse."),
        ('reverse', "Reverse", "Plays a sound reversed"),
        ('sum', "Sum", "Sums the samples of a sound."),
        (None),
        ('resample', "Resample", "Resamples the sound.")

    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='limit'
        , update=lambda self, context: self.operation_update())

    def init(self, context):
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new('SoundSampleSocketType', "Sample")
        float1_start_s = self.inputs.new("FloatSocketType", "start")
        float2_end_s = self.inputs.new("FloatSocketType", "end")
        self.inputs.new("FloatSocketType", "frequency")
        q = self.inputs.new("FloatSocketType", "Q")
        self.inputs.new("FloatSocketType", "length")
        self.inputs.new("FloatSocketType", "time")
        self.inputs.new("FloatSocketType", "attack")
        self.inputs.new("FloatSocketType", "release")
        self.inputs.new("FloatSocketType", "threshold")
        self.inputs.new("FloatSocketType", "arthreshold")
        self.inputs.new("FloatSocketType", "decay")
        self.inputs.new("FloatSocketType", "sustain")
        self.inputs.new("FloatSocketType", "factor")
        self.inputs.new("IntSocketType", "count")
        s_r_s = self.inputs.new("IntSocketType", "sample rate")
        self.inputs.new("IntSocketType", "quality")
        self.inputs.new('BoolSocketType', "additive")
        self.inputs.new('SoundSampleSocketType', "Sample")
        self.toggle_sockets(self.inputs[1:], True)
        self.toggle_sockets([float1_start_s, float2_end_s], False)
        super().init(context)
        q.input_value = 0.5
        s_r_s.input_value = 48000

    def toggle_sockets(self, sockets, hide):
        for socket in sockets:
            socket.hide = hide
            socket.hide_value = hide

    def execute_sound_functions(self, function_name, sockets):
        self.toggle_sockets(sockets, False)
        if self.inputs[0].input_value != "":
            parent_sample = Data.uuid_data_storage[self.inputs[0].input_value]
        else:
            parent_sample = None
        if parent_sample:
            values = []
            sample_function = getattr(parent_sample, function_name)
            for socket in sockets:
                if socket.bl_idname != "SoundSampleSocketType":
                    values.append(socket.input_value)
                else:
                    values.append(Data.uuid_data_storage[socket.input_value])

            if function_name in ('modulate', 'mix', 'join'):
                if not self.inputs[0].is_linked:
                    return None
                if self.inputs[0].is_linked and not sockets[0].is_linked:
                    return None
            return sample_function(*values).cache()
        else:
            return None

    def operation_update(self):
        sample_s = self.inputs[0]
        float1_start_s = self.inputs[1]
        float2_end_s = self.inputs[2]
        float3_frequency_s = self.inputs[3]
        float4_q_s = self.inputs[4]
        float5_length_s = self.inputs[5]
        float6_time_s = self.inputs[6]
        float7_attack_s = self.inputs[7]
        float8_release_s = self.inputs[8]
        float9_threshold_s = self.inputs[9]
        float10_arthreshold_s = self.inputs[10]
        float11_decay_s = self.inputs[11]
        float12_sustain_s = self.inputs[12]
        float13_factor_s = self.inputs[13]
        int1_count_s = self.inputs[14]
        int2_sample_rate_s = self.inputs[15]
        int3_quality_s = self.inputs[16]
        bool_additive_s = self.inputs[17]
        sample2_s = self.inputs[18]
        self.toggle_sockets(self.inputs[1:], True)
        sockets = []
        if self.operation == 'accumulate':
            sockets = [bool_additive_s]
        #        elif self.operation in ('pingpong', 'reverse', 'sum'):
        #            sockets = []
        elif self.operation in ('modulate', 'mix', 'join'):
            sockets = [sample2_s]
        elif self.operation == 'envelope' or self.operation == 'ADSR':
            sockets = [float7_attack_s, float8_release_s, float9_threshold_s, float10_arthreshold_s]
            if self.operation == "ADSR":
                sockets = [float7_attack_s, float11_decay_s, float12_sustain_s, float8_release_s]
        elif self.operation in ('fadein', 'fadeout', 'limit'):
            sockets = [float1_start_s, float5_length_s]
            if self.operation == "limit":
                if float1_start_s.input_value < 0:
                    float1_start_s.input_value = 0
                if float2_end_s.input_value < 0:
                    float2_end_s.input_value = 0
                if float2_end_s.input_value > 3600:
                    float2_end_s.input_value = 3600
                sockets = [float1_start_s, float2_end_s]
        elif self.operation == 'loop':
            if int1_count_s.input_value < 0:
                int1_count_s.input_value = 0
            sockets = [int1_count_s]
        elif self.operation in ('highpass', 'lowpass'):
            # recursion
            # float2_s.input_value = 0.5
            sockets = [float3_frequency_s, float4_q_s]
        elif self.operation in ('pitch', 'volume', 'threshold', 'delay'):
            sockets = [float13_factor_s]
            if self.operation == 'delay':
                sockets = [float6_time_s]
        elif self.operation == 'resample':
            sockets = [int2_sample_rate_s, int3_quality_s]

        new_sample = self.execute_sound_functions( self.operation, sockets)
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
        self.socket_update_disabled = True
        super().copy(node)
        self.inputs[0].input_value = ""
        self.inputs[18].input_value = ""
        self.operation = node.operation
        for i , old_sock in enumerate(node.inputs):
            self.inputs[i].input_value = node.inputs[i].input_value
        self.socket_update_disabled = False

    def socket_update(self, socket):
        if IS_DEBUG:
            super().log("socket_update")
            if self.socket_update_disabled:
                print("socket_update_disabled")
        if not self.socket_update_disabled:
            if socket != self.outputs[0]:
                self.operation_update()

    def update(self):
        super().update()
        if len(self.inputs) > 0:
            if not self.inputs[0].is_linked:
                self.inputs[0].input_value = ""

    #def refresh_outputs(self):
