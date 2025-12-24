from ..basic_nodes import ObmConstantNode


class VectorNode(ObmConstantNode):
    '''3-D Vector Node'''
    bl_idname = 'ObmVectorNodeType'
    bl_label = "Vector"


    def init(self, context):
        out_sock = self.outputs.new('FloatVectorSocketType', "Float")
        out_sock.is_constant = True
        super().init(context)

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        #self.outputs[0].input_value = node.outputs[0].input_value
        self.socket_update_disabled = False