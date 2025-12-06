import aud
import bpy

from ..basic_nodes import ObmSampleNode
from ...core.constants import IS_DEBUG
from ...core.global_data import Data
import mathutils


class OscillatorNode(ObmSampleNode):
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
        , update=lambda self, context: self.__operation_update())

    prev_frequency: bpy.props.FloatProperty(default=0.0)

    color_tag = 'INTERFACE'
    color = mathutils.Color((1.0, 1.0, 1.0))

    def __sound_function(self):
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

    def __operation_update(self):
        if self.operation == "SILENCE":
            # self.prev_frequency = self.inputs[1].input_value
            # self.inputs.remove(self.inputs[1])
            self.inputs[1].hide = True
            self.inputs[1].hide_value = True
        elif self.operation != "SILENCE":
            self.inputs[1].hide = False
            self.inputs[1].hide_value = False
        self.socket_update(self.inputs[0])
        super().init(self)

    def init(self, context):
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new("IntSocketType", "rate")
        self.inputs.new("FloatSocketType", "frequency")
        # self.inputs.new("NodeSocketFloat", "Frequency")
        self.inputs[0].input_value = 44100
        self.inputs[1].input_value = 110.0
        super().init(context)
        color_tag = 'INTERFACE'
        color = mathutils.Color((1.0, 1.0, 1.0))

    # Additional buttons displayed on the node.

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.outputs[0].input_value)
        layout.prop(self, "operation", text="Operation")

    def state_update(self):
        super().state_update()
        self.__sound_function()
