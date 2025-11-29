from ..basic_nodes import ObmConstantNode
from ...sockets.basic_sockets import SoundSocket
import bpy

class SpeakerNode(ObmConstantNode):
    '''Speaker Node'''
    bl_idname = 'SpeakerNodeType'
    bl_label = 'Speaker'
    bl_icon = 'SPEAKER'
    def init(self, context):
        speaker_socket = self.outputs.new('SpeakerSocketType', "Speaker")
        speaker_socket.is_constant = True
        super().init(context)
