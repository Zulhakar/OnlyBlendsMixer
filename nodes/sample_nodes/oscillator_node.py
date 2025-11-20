import uuid
import aud
import bpy

from ..basic_nodes import ObmSoundNode
from ...constants import SOUND_SOCKET_SHAPE, IS_DEBUG
from ...global_data import Data

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

        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

        self.outputs[0].input_value = self.node_uuid
        # Data.uuid_data_storage[self.node_uuid] =  aud.Sound.sine(44100)
        Data.uuid_data_storage[self.node_uuid] = aud.Sound.silence(44100).limit(0, 0.2)
        super().init(context)

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
        super().init(self)
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
        if super().insert_link(link) is None:
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
        if not self.mute:
            super().socket_update(socket)
            if not socket.is_output:
                self.refresh_outputs()
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
                    link.to_node.update_obm()
