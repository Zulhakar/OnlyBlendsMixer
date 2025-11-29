import aud
import bpy

from ..basic_nodes import ObmSampleNode
from ...constants import SOUND_SOCKET_SHAPE, IS_DEBUG
from ...global_data import Data

class NoteSequenceToSampleNode(ObmSampleNode):
    '''Sound Sample  which can be modified, played and recorded'''

    bl_idname = 'NoteSequenceToSampleNodeType'
    bl_label = "Note Sequence To Sample"
    node_uuid: bpy.props.StringProperty()



    def init(self, context):
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.outputs.new("FloatSocketType", "Frequency")
        self.inputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new("FloatVectorFieldSocketType", "Note")

        super().init(context)
        self.outputs[1].default_value = 1.0
        self.inputs[1].display_shape = "DIAMOND"
        # frequency duration intensity
        pips = self.inputs[1].input_value.add()
        pips.value = (110.0, 2.0, 1.0)
        pips = self.inputs[1].input_value.add()
        pips.value = (0.0, 0.5, 0.0)
        pips = self.inputs[1].input_value.add()
        pips.value = (210.0, 1.0, 0.5)
        #self.inputs[3].input_value = ((1.0, 1.0, 1.0), (1.0, 1.0, 2.0))
        #self.inputs[2].display_shape = "LIST"
        #print(self.inputs[2].inferred_structure_type)
    # Additional buttons displayed on the node.

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.outputs[0].input_value)

    def __create_sample_sequence(self):
        if len(self.inputs) > 1 and len(self.outputs) > 1:
            input_sample_socket = self.inputs[0]
            input_notes_socket = self.inputs[1]
            output_sample_socket = self.outputs[0]
            output_frequency_socket = self.outputs[1]
            if input_sample_socket.input_value != "" and len(input_notes_socket.input_value) > 0 and output_frequency_socket.is_linked:
                print("Note Sequence To Sample: is valid")
                for item in input_notes_socket.input_value:
                    print(item.value)
                    frequency, duration, intensity = item.value

            else:
                print("Not working")

    def state_update(self):
        super().state_update()
        self.__create_sample_sequence()