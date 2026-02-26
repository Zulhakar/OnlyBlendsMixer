import bpy
import numpy as np
from ..mixer_node import ObmSampleNode
from ...config import IS_DEBUG, OB_TREE_TYPE
from ...base.global_data import Data


def point_cloud(ob_name, coords):
    """Create point cloud object based on given coordinates and name."""
    me = bpy.data.meshes.new(ob_name + "Mesh")
    ob = bpy.data.objects.new(ob_name, me)
    me.from_pydata(coords, [], [])
    # ob.show_name = True
    me.update()
    return ob, me


class SampleToObjectNode(ObmSampleNode, bpy.types.Node):
    '''Generate Mesh from Sound Sample'''
    bl_label = "Sample To Object"
    last_file_name: bpy.props.StringProperty(default="")

    def init(self, context):
        self.inputs.new("NodeSocketSample", "Sample")
        self.inputs.new("NodeSocketFloatCnt", "Scale x-axis")
        self.inputs.new("NodeSocketStringCnt", "Name")
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

                self.__del_object_if_exit(self.last_file_name)
                if self.inputs[2].input_value != "":
                    file_name = self.inputs[2].input_value
                else:
                    file_name = self.name
                self.__del_object_if_exit(file_name)

                self.last_file_name = file_name

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

                    new_pc, mesh = point_cloud(file_name, coord)
                    bpy.context.collection.objects.link(new_pc)
                    new_pc.scale = (duration * scale, 1, 1)
                    channel_id += 1

    def socket_update(self, socket):
        super().socket_update(socket)
        self.__create_object()


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == OB_TREE_TYPE or ntree.bl_idname == "GeometryNodeTree"