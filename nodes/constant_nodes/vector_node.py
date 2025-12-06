from ..basic_nodes import ObmConstantNode


class VectorNode(ObmConstantNode):
    '''3-D Vector Node'''
    bl_idname = 'ObmVectorNodeType'
    bl_label = "Vector"


    def init(self, context):
        out_sock = self.outputs.new('FloatVectorSocketType', "Float")
        out_sock.is_constant = True
        super().init(context)