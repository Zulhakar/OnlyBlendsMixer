import aud
import bpy

from ..basic_nodes import ObmSampleNode
from ...core.constants import IS_DEBUG
from ...core.global_data import Data
import mathutils


class OscillatorSampleNode(ObmSampleNode):
    '''Oscillator to create synthetic sounds. Output is a Sample Socket with infinit duration.'''

    bl_label = "Oscillator"
    waveform_enums = [
        ('SAWTOOTH', "sawtooth", "Creates a sawtooth sound which plays a sawtooth wave."),
        ('SILENCE', "silence", "Creates a silence sound which plays simple silence."),
        ('SINE', "sine", "Creates a sine sound which plays a sine wave."),
        ('SQUARE', "square", "Creates a square sound which plays a square wave."),
        ('TRIANGLE', "triangle", "Creates a triangle sound which plays a triangle wave."),
    ]
    waveform_selection: bpy.props.EnumProperty(  # type: ignore
        name="Waveform"
        , items=waveform_enums
        , default='SINE'
        , update=lambda self, context: self.waveform_selection_update())


    def waveform_selection_update(self):
        new_sample = None
        if self.inputs[0].input_value > 192000:
            self.inputs[0].input_value = 192000
        if self.waveform_selection == "SILENCE":
            self.inputs[1].hide = True
            self.inputs[1].hide_value = True
            new_sample = aud.Sound.silence(self.inputs[0].input_value)
        elif self.waveform_selection != "SILENCE":
            self.inputs[1].hide = False
            self.inputs[1].hide_value = False
        if self.waveform_selection == "SINE":
            new_sample = aud.Sound.sine(self.inputs[1].input_value, self.inputs[0].input_value)
        elif self.waveform_selection == "SQUARE":
            new_sample = aud.Sound.square(self.inputs[1].input_value, self.inputs[0].input_value)
        elif self.waveform_selection == "TRIANGLE":
            new_sample = aud.Sound.triangle(self.inputs[1].input_value, self.inputs[0].input_value)
        elif self.waveform_selection == "SAWTOOTH":
            new_sample = aud.Sound.sawtooth(self.inputs[1].input_value, self.inputs[0].input_value)

        self.socket_update_disabled = True
        if self.inputs[2].input_value > 3600:
            self.inputs[2].input_value = 3600
        if self.inputs[2].input_value < 0:
            self.inputs[2].input_value = 0
        self.socket_update_disabled = False
        if self.inputs[2].input_value <= 0.0:
            new_sample = aud.Sound.silence(self.inputs[0].input_value)
            new_sample = new_sample.limit(0.0, 0.01)
        else:
            new_sample = new_sample.limit(0.0, self.inputs[2].input_value)
        Data.uuid_data_storage[self.node_uuid] = new_sample
        self.outputs[0].input_value = self.node_uuid
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value

    def init(self, context):
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new("IntSocketType", "rate")
        self.inputs.new("FloatSocketType", "frequency")
        self.inputs.new("FloatSocketType", "length")
        super().init(context)
        self.inputs[0].input_value = 48000
        self.inputs[1].input_value = 110.0
        self.inputs[2].input_value = 1.0
        self.waveform_selection_update()

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.outputs[0].input_value)
        layout.prop(self, "waveform_selection", text="Waveform")

    def socket_update(self, socket):
        super().socket_update(socket)
        if not self.socket_update_disabled:
            if socket != self.outputs[0]:
                self.waveform_selection_update()

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.socket_update_disabled = False
