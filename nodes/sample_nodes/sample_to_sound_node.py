import uuid

import bpy

from ..basic_nodes import ObmSoundNode
from ...sockets.basic_sockets import ObmStringSocket
from ...constants import SOUND_SOCKET_SHAPE
from ...global_data import Data

class SampleToSoundNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Transform Sample to Sound'''

    bl_idname = 'SampleToSoundNodeType'
    bl_label = "Sample To Sound"
    # update=lambda self, context: self.update_sound_prop(),
    node_uuid: bpy.props.StringProperty()


    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs.new("StringSocketType", "File Name")
        self.inputs.new("IntSocketType", "Sample Rate")
        self.inputs[2].input_value = 44100
        self.outputs.new('SoundSocketType', "Sound")
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

    def store_data(self):


        if self.inputs[0].input_value != "" and self.inputs[0].is_linked:
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            data_path = self.inputs[1].input_value
            sample_rate = self.inputs[2].input_value
            print("data_path")
            print(data_path)
            sound_sample.write(data_path, sample_rate, 1)
            print("write")
            self.outputs[0].input_value = bpy.data.sounds.load(data_path, check_existing=True)
            print("Soundblock erstellt:",  self.outputs[0].input_value.name)

        else:
            print("NOT")

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Infos")
        layout.label(text=self.inputs[1].input_value)
        if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
            layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            # r = layout.row()
            # r.prop(self, 'import_path', text="")
            # layout.label(text="Path: " + self.outputs[0].default_value)
            # layout.label(text="Blender Path: " + self.outputs[1].default_value)
            # layout.label(text="Channels: " + self.outputs[2].default_value)
            # layout.label(text="Samplerate: " + str(self.outputs[3].default_value))
            # r.label(text="Path: " + self.outputs[0].default_value)

    def refresh_outputs(self):
        print("refresh outputs")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        print(link)


        if link.to_socket.type != link.from_socket.type:
            #self.error_message_set("Falscher Socket-Typ!")
            print("Wrong Socket ", str(link.from_socket.type))
        else:
            #self.error_message_clear()
            self.store_data()

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        super().socket_update(socket)
        print("socket_update sample_to_sound")
        print(socket)
        if isinstance(socket, ObmStringSocket):
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
