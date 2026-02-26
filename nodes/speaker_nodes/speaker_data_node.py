import bpy
from ...nodes.mixer_node import ObmSoundNode


def strip_frame_start_end_changed(*args):
    self = args[0]
    strip = args[1]
    self.outputs[0].input_value = strip.frame_end - strip.frame_start


class SpeakerDataNode(ObmSoundNode,  bpy.types.Node):
    '''Speaker Data Node to get data from Speaker'''
    bl_label = "Speaker Data"
    bl_icon = 'OUTLINER_DATA_SPEAKER'

    def init(self, context):
        self.inputs.new('NodeSocketSpeaker', "Speaker")
        self.outputs.new('NodeSocketFloatCnt', "Strip Length")
        self.outputs.new('NodeSocketFloatCnt', "Volume")
        self.outputs.new('NodeSocketFloatCnt', "Pitch")
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
                # key=(bpy.types.NlaStrip, "frame_end_ui"),
                owner=self,
                args=(self, strip,),
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
            super().socket_update(socket)
            self.speaker_update()
            self.get_speaker_data()
        elif socket == self.outputs[0]:
            super().socket_update(socket)
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value

    def refresh_outputs(self):
        self.log("refresh_outputs")
        self.speaker_update()
        self.get_speaker_data()