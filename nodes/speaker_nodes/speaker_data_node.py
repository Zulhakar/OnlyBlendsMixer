import bpy
from ...nodes.mixer_node import ObmSoundNode
from ...cnt.base.global_data import Data
from ...config import IS_DEBUG
import uuid

def strip_frame_start_end_changed(*args):
    self = args[0]
    strip = args[1]
    if self:
        self.outputs[0].input_value = strip.frame_end - strip.frame_start


class SpeakerDataNode(ObmSoundNode,  bpy.types.Node):
    '''Speaker Data Node to get data from Speaker'''
    bl_label = "Speaker Data"
    bl_icon = 'OUTLINER_DATA_SPEAKER'
    uuid_msg_bus: bpy.props.StringProperty()


    def init(self, context):
        self.inputs.new('NodeSocketSpeaker', "Speaker")
        self.outputs.new('NodeSocketFloatCnt', "Strip Length")
        self.outputs.new('NodeSocketFloatCnt', "Volume")
        self.outputs.new('NodeSocketFloatCnt', "Pitch")
        self.uuid_msg_bus = str(uuid.uuid4()).replace("-", "")
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
        bpy.msgbus.clear_by_owner(Data.uuid_message_bus[self.uuid_msg_bus])
        del Data.uuid_message_bus[self.uuid_msg_bus]

    def speaker_update(self):
        speaker = self.inputs[0].input_value
        if speaker is not None and speaker.name in bpy.data.objects:
            strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips[0]
            msg_bus_obj = object()
            Data.uuid_message_bus[self.uuid_msg_bus] = msg_bus_obj
            bpy.msgbus.subscribe_rna(
                key=strip.path_resolve("frame_end_ui", False),
                # key=(bpy.types.NlaStrip, "frame_end_ui"),
                owner=msg_bus_obj,
                args=(self, strip,),
                notify=strip_frame_start_end_changed,
                options={'PERSISTENT'}
            )
            bpy.msgbus.subscribe_rna(
                key=strip.path_resolve("frame_start_ui", False),
                owner=msg_bus_obj,
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
        if IS_DEBUG:
            self.log("refresh")
        self.speaker_update()
        self.get_speaker_data()