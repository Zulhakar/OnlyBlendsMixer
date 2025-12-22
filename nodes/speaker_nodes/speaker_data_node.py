import bpy

from ...core.global_data import Data
from ...nodes.basic_nodes import ObmConstantNode
from ...core.helper import get_length_and_specs_from_sound
from ...core.constants import IS_DEBUG


def strip_frame_start_end_changed(*args):
    self = args[0]
    strip = args[1]
    self.outputs[0].input_value = strip.frame_end - strip.frame_start

class SpeakerDataNode(ObmConstantNode):
    '''Speaker Data Node to get data from Speaker'''
    bl_label = "Speaker Data"
    bl_icon = 'OUTLINER_DATA_SPEAKER'

    def init(self, context):
        self.inputs.new('SpeakerSocketType', "Speaker")
        self.outputs.new('FloatSocketType', "Strip Length")
        self.outputs.new('FloatSocketType', "Volume")
        self.outputs.new('FloatSocketType', "Pitch")
        super().init(context)

    def get_speaker_data(self):
        speaker = self.inputs[0].input_value
        if speaker is not None and speaker.name in bpy.data.objects:
            strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips[0]
            length = strip.frame_end - strip.frame_start
            self.outputs[0].input_value = length
            self.outputs[1].input_value = speaker.volume
            self.outputs[2].input_value = speaker.pitch

    def free(self):
        super().free()
        bpy.msgbus.clear_by_owner(self)



    def speaker_update(self):
        speaker = self.inputs[0].input_value
        if speaker is not None and speaker.name in bpy.data.objects:
            strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips[0]
            bpy.msgbus.subscribe_rna(
                 key=strip.path_resolve("frame_end_ui", False),
                #key=(bpy.types.NlaStrip, "frame_end_ui"),
                owner=self,
                args=(self,strip,),
                notify=strip_frame_start_end_changed,
                options={'PERSISTENT'}
            )
            bpy.msgbus.subscribe_rna(
                key=strip.path_resolve("frame_start_ui", False),
                owner=self,
                args=(self, strip,),
                notify=strip_frame_start_end_changed,
                options={'PERSISTENT'}
            )
    def socket_update(self, socket):
        if socket == self.inputs[0]:
            self.speaker_update()
            self.get_speaker_data()
            super().socket_update(socket)
        elif socket == self.outputs[0]:
            super().socket_update(socket)
