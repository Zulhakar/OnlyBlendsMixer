import bpy
import aud
import tempfile
import os
from ..basic_nodes import ObmSoundNode
from ...core.global_data import Data


def get_sample_rates():
    sample_rates = []
    all_members = aud.__dict__
    for member in all_members:
        if member.startswith("RATE_") and not member.startswith("RATE_INVALID"):
            sample_rates.append((member, member.split("_")[1], ""))
    return sample_rates


def get_container_types():
    container_types = []
    all_members = aud.__dict__
    for member in all_members:
        if member.startswith("CONTAINER_") and not member.startswith("CONTAINER_INVALID"):
            container_types.append((member, member.split("_")[1], ""))
    return container_types


class SampleToSoundNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Transform a Sample to Sound which can be used with a Speaker Node'''

    bl_label = "Sample To Sound"
    bl_icon = 'FILE_SOUND'

    sample_rate_selection: bpy.props.EnumProperty(  # type: ignore
        name="Sample Rates"
        , items=get_sample_rates()
        , default='RATE_48000'
        , update=lambda self, context: self.sample_rate_update()
    )
    container_selection: bpy.props.EnumProperty(  # type: ignore
        name="Container"
        , items=get_container_types()
        # , default='RATE_48000'
        , update=lambda self, context: self.container_update()
    )

    def sample_rate_update(self):
        sample_rate_socket = self.inputs[1]
        sample_rate_socket.input_value = getattr(aud, self.sample_rate_selection)
        # self.store_data()

    def container_update(self):
        self.store_data()

    def draw_buttons(self, context, layout):
        layout.prop(self, "sample_rate_selection", text="Rate")
        layout.prop(self, "container_selection", text="Container")

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sample")
        sample_rate = self.inputs.new("IntSocketType", "Sample Rate")
        self.outputs.new('SoundSocketType', "Sound")
        sample_rate.input_value = 48000
        super().init(context)

    def store_data(self):
        if (self.inputs[0] and self.inputs[0].input_value and self.inputs[0].input_value != "" and
                self.inputs[0].input_value in Data.uuid_data_storage and Data.uuid_data_storage[
                    self.inputs[0].input_value]):
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            sample_rate = self.inputs[1].input_value
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"{self.name}")
            sound_sample.write(tmp_path, rate=getattr(aud, self.sample_rate_selection), container=getattr(aud,
                                                                                                          self.container_selection))  # , aud.RATE_44100, aud.CHANNELS_MONO, aud.FORMAT_S32, aud.CONTAINER_MP3, aud.CODEC_MP3)
            new_data = bpy.data.sounds.load(tmp_path, check_existing=True)
            self.outputs[0].input_value = new_data

        else:
            if self.outputs[0].input_value is not None:
                self.outputs[0].input_value.user_clear()
                bpy.data.sounds.remove(self.outputs[0].input_value)
            self.outputs[0].input_value = None
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value

    def free(self):
        super().free()
        sound = self.outputs[0].input_value
        if sound:
            sound.user_clear()
            bpy.data.sounds.remove(sound)

    def refresh_outputs(self):
        super().refresh_outputs()
        self.store_data()

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0] or socket == self.inputs[1]:
            self.store_data()
