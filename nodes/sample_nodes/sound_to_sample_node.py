import bpy
import aud
import tempfile
import os
from ..mixer_node import ObmSampleNode
from ...config import IS_DEBUG
from ...base.global_data import Data

class SoundToSampleNode(ObmSampleNode):
    bl_label = "Sound To Sample"

    def init(self, context):
        self.outputs.new('NodeSocketSample', "Sample")
        self.inputs.new("NodeSocketSoundObm", "Sound")
        super().init(context)

    def socket_update(self, socket):
        if IS_DEBUG:
            super().log("socket_update")
        if not socket.is_output:

            Data.uuid_data_storage[self.node_uuid] = aud.Sound.file(socket.input_value.filepath)
            self.outputs[0].input_value = self.node_uuid
        else:
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.node_uuid