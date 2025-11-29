import bpy
import tempfile
import os
from ..basic_nodes import ObmSoundNode
from ...sockets.basic_sockets import ObmStringSocket
from ...global_data import Data


class SampleToSoundNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Transform Sample to Sound'''

    bl_idname = 'SampleToSoundNodeType'
    bl_label = "Sample To Sound"
    bl_icon = 'FILE_SOUND'

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sample")
        sample_rate = self.inputs.new("IntSocketType", "Sample Rate")
        self.outputs.new('SoundSocketType', "Sound")
        sample_rate.input_value = 44100
        super().init(context)

    def store_data(self):
        sample_socket = self.inputs[0]
        sound_socket = self.outputs[0]
        if sample_socket.input_value != "":
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            sample_rate = self.inputs[1].input_value
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"{self.name}.wav")
            sound_sample.write(tmp_path, sample_rate, 1)
            sound_socket.input_value = bpy.data.sounds.load(tmp_path, check_existing=True)
            print("Soundblock erstellt:", self.outputs[0].input_value.name)

        else:
            print("no sample")
            #if sound is not None:
            #    sound.user_clear()
            #    bpy.data.sounds.remove(sound)
            self.outputs[0].input_value = None

    # Free function to clean up on removal.
    def free(self):
        super().free()
        sound = self.outputs[0].input_value
        sound.user_clear()
        bpy.data.sounds.remove(sound)

    def refresh_outputs(self):
        super().refresh_outputs()
        self.store_data()

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        super().insert_link(link)
        if link.is_valid:
            if link.to_socket == self.inputs[0]:
                self.inputs[0].input_value = link.from_socket.input_value
                self.store_data()
            if link.to_socket == self.inputs[1]:
                if self.inputs[0].input_value is not None and self.inputs[0].input_value != "":
                    self.store_data()
        else:
            pass
            #print(link.is_valid)


    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        super().socket_update(socket)
        if socket == self.inputs[0] or socket == self.inputs[1]:
            if self.inputs[0].is_linked:
                self.store_data()
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
                    link.to_node.update_obm()
        else:
            print("no update")

    def update(self):
        super().update()

    def update_obm(self):
        super().update_obm()
        self.store_data()
        for link in self.outputs[0].links:
            link.to_node.update_obm()
    # def update(self):
    #     super().update()
    #     if not self.inputs[0].is_linked:
    #         self.inputs[0].input_value = ""
    #     self.refresh_outputs()
    #
    # def update_obm(self):
    #     self.update()
    #     for link in self.outputs[0].links:
    #         # link.to_node.update_obm(self, self.outputs[0])
    #         link.to_node.update_obm()
