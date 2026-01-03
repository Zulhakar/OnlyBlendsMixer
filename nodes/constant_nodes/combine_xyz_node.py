from ..basic_nodes import ObmConstantNode


class CombineXyzNode(ObmConstantNode):
    '''3-D Vector Node'''
    bl_idname = 'ObmCombineXyzNodeType'
    bl_label = "Combine XYZ"


    def init(self, context):
        self.outputs.new('FloatVectorSocketType', "Float")
        self.inputs.new('FloatSocketType', 'X')
        self.inputs.new('FloatSocketType', 'Y')
        self.inputs.new('FloatSocketType', 'Z')
        super().init(context)

    def socket_update(self, socket):
        if socket.name in self.inputs:
            for i, input in enumerate(self.inputs):
                if input == socket:
                    self.outputs[0].input_value[i] = socket.input_value
            super().socket_update(socket)

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.socket_update_disabled = False
