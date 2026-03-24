import bpy
import aud
import numpy as np
from ...config import IS_DEBUG
from ..mixer_node import ObmSampleNode
from ...base.global_data import Data


class ObjectToSampleNode(ObmSampleNode):
    bl_label = "Object To Sample"

    domain_enums = [
        ('POINTCLOUD', "Point Cloud", "Use Pointcloud Domain from Geometry data to create a Sample"),
        ('MESH', "Mesh", "Use Mesh Domain from Geometry data to create a Sample"),

    ]
    domain: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=domain_enums
        , default='MESH'
        , update=lambda self, context: self.domain_update(context))

    def init(self, context):
        self.inputs.new("NodeSocketObjectCnt", "Object")
        self.inputs.new("NodeSocketStringCnt", "Attribute")
        self.inputs.new("NodeSocketIntCnt", "Rate")
        self.inputs.new("NodeSocketIntCnt", "Axis")
        self.outputs.new("NodeSocketSample", "Sample")
        self.inputs[3].input_value = 0
        self.inputs[2].input_value = 48000
        super().init(context)

    def domain_update(self, context):
        sample = self.get_object_data()
        if sample:
            Data.uuid_data_storage[self.node_uuid] = sample
            self.outputs[0].input_value = self.node_uuid

    def get_object_data(self):
        obj = self.inputs[0].input_value
        sample_rate = self.inputs[2].input_value
        attr_name = self.inputs[1].input_value
        axis = self.inputs[3].input_value
        if obj and attr_name != "":

            # if it is normal object
            # attr = obj.data.attributes.get(attr_name)

            # sample_rate = self.inputs[1].input_value
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = depsgraph.id_eval_get(obj)
            if obj_eval.is_evaluated:
                geometry = obj_eval.evaluated_geometry()
                if self.domain == "POINTCLOUD":
                    domain_data = geometry.pointcloud
                elif self.domain == "MESH":
                    domain_data = geometry.mesh
                else:
                    domain_data = None
                    return None

                if attr_name in domain_data.attributes:
                    selected_attr = domain_data.attributes[attr_name]

                    if selected_attr is not None:
                        n = len(selected_attr.data)
                        if n > 0:
                            track = []
                            values = selected_attr.data.values()

                            if selected_attr.data_type == 'FLOAT_VECTOR' and 0 <= axis <= 2 :
                                for val in values:
                                    track.append(val.vector[axis])
                            elif selected_attr.data_type == 'FLOAT':
                                for val in values:
                                    track.append(val.value)
                            else:
                                return None
                            sound_array = np.asarray([track]).T.astype(np.float32)
                            sound_sample = aud.Sound.buffer(sound_array, sample_rate)
                            return sound_sample
                        else:
                            return None
                else:
                    return None

    def draw_buttons(self, context, layout):
        if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
            layout.label(text="Length: " + str(Data.uuid_data_storage[self.node_uuid].length))
        layout.prop(self, "domain", text="")

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            sample = self.get_object_data()
            if sample:
                Data.uuid_data_storage[self.node_uuid] = sample
                self.outputs[0].input_value = self.node_uuid
        else:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value

    def refresh(self):
        if IS_DEBUG:
            self.log("refresh")
        sample = self.get_object_data()
        if sample:
            Data.uuid_data_storage[self.node_uuid] = sample
            self.outputs[0].input_value = self.node_uuid
