import bpy
from ..mixer_node import ObmSampleNode


class ObjectTrackNode(ObmSampleNode):

    bl_label = "Object Track "

    def init(self, context):
        self.inputs.new("NodeSocketObjectCnt", "Object")
        self.inputs.new("NodeSocketSample", "Sample")
        self.inputs.new("NodeSocketStringCnt", "Starttime Attribute")
        self.inputs.new("NodeSocketStringCnt", "Duration Attribute")
        self.inputs.new("NodeSocketStringCnt", "Volume Attribute")
        self.inputs.new("NodeSocketStringCnt", "Note Attribute")
        self.outputs.new("NodeSocketSample", "Sample")
        super().init(context)


    def get_attributes(self, domain="POINTCLOUD"):
        obj = self.inputs[0].input_value
        depsgraph = bpy.context.evaluated_depsgraph_get()

        obj_eval = depsgraph.id_eval_get(obj)
        # self.node_tree.interface.active.hide_in_modifier = True
        # self.node_tree.interface.active.hide_in_modifier = False
        geometry = obj_eval.evaluated_geometry()
        domain_data = None
        if domain == "POINTCLOUD":
            domain_data = geometry.pointcloud
        elif domain == "MESH":
            domain_data = geometry.mesh
        if domain_data is None:
            return None



        attr_list = ["start_time", "duration", "volume", "note"]
        st_attr = domain_data.attributes[attr_list[0]]
        n = len(st_attr.data)
        attr_dict = {}
        for attr in attr_list:
            attr_dict[attr] = domain_data.attributes[attr].data.values()
        sequence = []
        for i in range(0, n):
            pack = []
            for attr in attr_list:
                value = attr_dict[attr][i]
                pack.append(value.value)
            sequence.append(pack)
        print(sequence)

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0]:
            self.get_attributes()
