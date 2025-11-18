from ...nodes.basic_nodes import ObmConstantNode
from ...sockets.basic_sockets import SoundSocket
class SpeakerNode(ObmConstantNode):
    '''Speaker Node'''
    bl_idname = 'SpeakerNodeType'
    bl_label = "Speaker"

    def init(self, context):
        self.outputs.new('SpeakerSocketType', "Speaker")
        self.inputs.new('SoundSocketType', "Sound")
        self.inputs.new('FloatSocketType', "Volume")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        speaker = self.outputs[0].input_value
        sound = self.inputs[0].input_value
        volume = self.inputs[1].input_value
        if socket == self.inputs[0]:
            if isinstance(socket, SoundSocket):
                print("Sound Socket Changed")
            if self.inputs[0].is_linked:
                speaker.sound = sound

        if self.inputs[1].is_linked:
            speaker.volume = self.inputs[1].input_value
