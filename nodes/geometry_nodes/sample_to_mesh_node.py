import bpy
from ..basic_nodes import ObmSoundNode
from ...core.constants import SAMPLE_TO_MESH_NODE_DESCRIPTION, IS_DEBUG
from ...core.global_data import Data
import numpy as np


def point_cloud(ob_name, coords):
    """Create point cloud object based on given coordinates and name."""
    me = bpy.data.meshes.new(ob_name + "Mesh")
    ob = bpy.data.objects.new(ob_name, me)
    me.from_pydata(coords, [], [])
    # ob.show_name = True
    me.update()
    return ob


class SampleToMeshNode(ObmSoundNode, bpy.types.Node):
    '''Generate Mesh from Sound Sample'''
    bl_idname = 'SampleToMeshType'
    bl_label = "Sample To Mesh"

    def init(self, context):
        self.inputs.new("SoundSampleSocketType", "Sample")
        self.inputs.new("FloatSocketType", "Scale x-axis")
        self.inputs[1].input_value = 1.0
        super().init(context)

    def __del_object_if_exit(self, object_name):
        if object_name in bpy.data.objects:
            obj = bpy.data.objects[object_name]
            bpy.data.objects.remove(obj, do_unlink=True)

    def __create_object(self):
        channel_id = 0
        # use_seperate_channels = self.inputs[3].input_value
        use_seperate_channels = False
        if self.inputs[0].input_value and self.inputs[0].input_value != "" and self.inputs[
            0].input_value in Data.uuid_data_storage:
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            if sound_sample:
                file_name = self.name
                sample_rate, channels = sound_sample.specs
                for i in range(0, channels):
                    object_name = f"{file_name}_channel_{i}"
                    self.__del_object_if_exit(object_name)
                self.__del_object_if_exit(f"{file_name}")

                if not use_seperate_channels:
                    sound_sample = sound_sample.rechannel(1)
                np_array_sound = sound_sample.data()

                sample_rate, channels = sound_sample.specs
                duration = sound_sample.length / sample_rate
                scale = self.inputs[1].input_value

                for channel in np_array_sound.T:
                    x = np.linspace(0, duration, len(channel))
                    z = np.zeros(len(channel))
                    coord = np.vstack([x, channel, z])
                    coord = coord.T
                    coord = coord.tolist()
                    if use_seperate_channels:
                        object_name = f"{file_name}_channel_{channel_id}"
                    else:
                        object_name = f"{file_name}"

                    new_pc = point_cloud(object_name, coord)
                    bpy.context.collection.objects.link(new_pc)
                    new_pc.scale = (duration * scale, 1, 1)
                    channel_id += 1

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0] or socket == self.inputs[1]:
            self.__create_object()
