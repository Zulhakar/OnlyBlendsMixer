import bpy

from ..basic_nodes import ObmConstantNode


class KeySequenceNode(ObmConstantNode):
    '''Key Sequence Node'''
    bl_idname = 'KeySequenceNodeType'
    bl_label = "Key Sequence"


    def init(self, context):
        self.outputs.new('FloatVectorFieldSocketType', "Vector Field")
        self.inputs.new("FloatVectorSocketType", "Key Press", use_multi_input=True)
        super().init(context)

    def insert_link(self, link):
        self.log("insert_link")
        if link.to_socket == self.inputs[0]:
            #for existing_links in self.inputs[0].links:
            #new_value = link.from_socket.input_value
            self.outputs[0].input_value.clear()
            for i, connected_link in enumerate(self.inputs[0].links):
                new_item = self.outputs[0].input_value.add()
                new_item.value = connected_link.from_socket.input_value
