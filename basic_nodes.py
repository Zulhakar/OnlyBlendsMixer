from bpy.types import NodeCustomGroup


class ObmSoundNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ObmSoundTreeType'


class ObjectNode(ObmSoundNode, NodeCustomGroup):
    '''Object Node'''
    bl_idname = 'ObmObjectNodeType'
    bl_label = "Object Node"

    # object_name =  bpy.props.StringProperty(update=)

    def init(self, context):
        self.inputs.new('ObjectSocketType', "Object")
        self.outputs.new('ObjectSocketType', "Object")
        print("shape")

    def socket_update(self, socket):
        print(socket)
        if not socket.is_output:
            self.outputs[0].input_value = self.inputs[0].input_value

class FloatNode(ObmSoundNode, NodeCustomGroup):
    '''Float Value Node'''
    bl_idname = 'ObmFloatNodeType'
    bl_label = "Float Node"
    # object_name =  bpy.props.StringProperty(update=)

    def init(self, context):
        #self.use_custom_color = True
        self.inputs.new('FloatSocketType', "Float")
        self.outputs.new('FloatSocketType', "Float")
    def update(self):
        print("update float")

    def socket_update(self, socket):
        print("float socket update node")
        if not socket.is_output:
            print("pups")
            self.outputs[0].input_value = socket.input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()
                #link.to_node.outputs[0].input_value = link.to_node.outputs[0].input_value
                print("pups")
    def socket_value_update(self, context):
        print("#######socket_value_update origin")

class IntNode(ObmSoundNode, NodeCustomGroup):
    '''Float Value Node'''
    bl_idname = 'ObmIntNodeType'
    bl_label = "Integer Node"

    # object_name =  bpy.props.StringProperty(update=)

    def init(self, context):
        self.inputs.new('IntSocketType', "Integer")
        self.outputs.new('IntSocketType', "Integer")

    def socket_update(self, socket):
        print(socket)
        if not socket.is_output:
            print("pups")
            self.outputs[0].input_value = socket.input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()

    def socket_value_update(self, context):
        print("#######socket_value_update origin")

class StringNode(ObmSoundNode, NodeCustomGroup):
    '''Float Value Node'''
    bl_idname = 'ObmStringNodeType'
    bl_label = "String Node"

    # object_name =  bpy.props.StringProperty(update=)

    def init(self, context):
        self.inputs.new('StringSocketType', "String")
        self.outputs.new('StringSocketType', "String")

    def socket_update(self, socket):
        print(socket)
        if not socket.is_output:
            print("pups")
            self.outputs[0].input_value = socket.input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                link.to_node.update_obm()

    def socket_value_update(self, context):
        print("#######socket_value_update origin")