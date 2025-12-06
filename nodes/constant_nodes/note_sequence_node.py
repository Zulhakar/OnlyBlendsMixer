import bpy

from ..basic_nodes import ObmConstantNode


class KeySequenceNode(ObmConstantNode):
    '''Key Sequence Node'''
    bl_idname = 'KeySequenceNodeType'
    bl_label = "Key Sequence"


    def init(self, context):
        out_sock = self.outputs.new('FloatVectorFieldSocketType', "Vector Field")
        self.inputs.new("FloatVectorSocketType", "Key Press", use_multi_input=True)
        super().init(context)

    def insert_link(self, link):
        if link.to_socket == self.inputs[0]:
            #for existing_links in self.inputs[0].links:
            new_value = self.outputs[0].input_value.add()
            new_value.value = link.from_socket.input_value
            print("§IIPWEIDR")