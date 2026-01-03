import bpy
from ..basic_nodes import ObmSoundNode

class NoteSequenceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Note Sequence Node'''
    bl_label = "Note Sequence"

    def init(self, context):
        self.outputs.new('FloatVectorFieldSocketType', "Vector Field")
        self.inputs.new("FloatVectorSocketType", "Key Press", use_multi_input=True)
        super().init(context)

    def insert_link(self, link):
        #is there an alternative way?
        super().insert_link(link)
        if link.is_valid:
            if link.to_socket == self.inputs[0]:
                self.outputs[0].input_value.clear()
                insert_index = len(self.inputs[0].links) - link.multi_input_sort_id
                for i, connected_link in enumerate(self.inputs[0].links):
                    if i == insert_index:
                        new_item = self.outputs[0].input_value.add()
                        new_item.value = link.from_socket.input_value
                    new_item = self.outputs[0].input_value.add()
                    new_item.value = connected_link.from_socket.input_value
                if insert_index == len(self.inputs[0].links):
                    new_item = self.outputs[0].input_value.add()
                    new_item.value = link.from_socket.input_value
                for l in self.outputs[0].links:
                    l.to_socket.input_value.clear()
                    for item in self.outputs[0].input_value:
                        new_item = l.to_socket.input_value.add()
                        new_item.value = item.value
                    #    print("#####:", str(new_item.value[0]))
                    # print("sock update2")
                    l.to_node.socket_update(l.to_socket)
            #for item in self.outputs[0].input_value:
            #    print(str(item.value[0]), str(item.value[1]), str(item.value[2]))



    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0]:
            self.outputs[0].input_value.clear()
            for i, connected_link in enumerate(self.inputs[0].links):
                new_item = self.outputs[0].input_value.add()
                new_item.value = connected_link.from_socket.input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value.clear()
                for item in self.outputs[0].input_value:
                    new_item = link.to_socket.input_value.add()
                    new_item.value = item.value

                if link.to_node.bl_idname != 'NodeGroupOutput':
                    link.to_node.socket_update(link.to_socket)
                else:
                    link.to_socket.update_prop()
        elif socket == self.outputs[0]:
            for link in self.outputs[0].links:
                link.to_socket.input_value.clear()
                for item in self.outputs[0].input_value:
                    new_item = link.to_socket.input_value.add()
                    new_item.value = item.value

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.socket_update_disabled = False