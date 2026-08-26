import bpy
import aud
import tempfile
import os
from ..mixer_node import ObmSoundNode
from ...config import IS_DEBUG
from ...base.global_data import Data

def get_container_types():
    container_types = []
    all_members = aud.__dict__
    for member in all_members:
        if member.startswith("CONTAINER_") and not member.startswith("CONTAINER_INVALID"):
            container_types.append((member, member.split("_")[1], ""))
    return container_types


class SampleToSoundNode(ObmSoundNode, bpy.types.Node):
    '''Transform a Sample to Sound which can be used with a Speaker Node'''

    bl_label = "Sample To Sound"
    bl_icon = 'FILE_SOUND'

    container_selection: bpy.props.EnumProperty(  # type: ignore
        name="Container"
        , items=get_container_types()
        , update=lambda self, context: self.container_update()
    )

    def container_update(self):
        self.store_data()

    def draw_buttons(self, context, layout):
        layout.prop(self, "container_selection", text="")

    def init(self, context):
        self.inputs.new('NodeSocketSample', "Sample")
        sample_rate = self.inputs.new("NodeSocketIntCnt", "Rate")
        self.outputs.new('NodeSocketSoundObm', "Sound")
        self.socket_update_disabled = True
        sample_rate.input_value = 48000
        self.socket_update_disabled = False
        super().init(context)

    def store_data(self):
        if (self.inputs[0] and self.inputs[0].input_value and self.inputs[0].input_value != "" and
                self.inputs[0].input_value in Data.uuid_data_storage and Data.uuid_data_storage[
                    self.inputs[0].input_value]):
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            sample_rate = self.inputs[1].input_value
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"{self.name}")
            sound_sample.write(tmp_path, rate=sample_rate, container=getattr(aud, self.container_selection))
            new_data = bpy.data.sounds.load(tmp_path, check_existing=True)
            self.outputs[0].input_value = new_data

        else:
            if self.outputs[0].input_value is not None:
                self.outputs[0].input_value.user_clear()
                bpy.data.sounds.remove(self.outputs[0].input_value)
            self.outputs[0].input_value = None

    def free(self):
        super().free()
        sound = self.outputs[0].input_value
        if sound:
            sound.user_clear()
            bpy.data.sounds.remove(sound)

    def recompute(self):
        self.store_data()

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0] or socket == self.inputs[1]:
            self.store_data()
        else:
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value