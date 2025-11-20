from bpy.types import NodeCustomGroup
from ..constants import IS_DEBUG, SINGLE_VALUES_SOCKET_SHAPE

class ObmSoundNode:

    def init(self, context):
        for output in self.outputs:
            if not output.is_multi_input:
                output.display_shape = SINGLE_VALUES_SOCKET_SHAPE
        for input in self.inputs:
            if not input.is_multi_input:
                input.display_shape = SINGLE_VALUES_SOCKET_SHAPE

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ObmSoundTreeType'

    def copy(self, node):
        if IS_DEBUG:
            print(f"Copying from node {self.bl_idname}")

    def free(self):
        if IS_DEBUG:
            print(f"Removing node {self.bl_idname}")

    def refresh_outputs(self):
        if IS_DEBUG:
            print(f"refresh outputs {self.bl_idname}")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        if IS_DEBUG:
            print(f"link {self.bl_idname}")
        if link.to_socket.type != link.from_socket.type:
            # self.error_message_set("Falscher Socket-Typ!")
            print("Wrong Socket ", str(link.from_socket.type))
            link.is_valid = False
        else:
            link.is_valid = True

    def update(self):
        if IS_DEBUG:
            print(f"update {self.bl_idname}")

    def socket_update(self, socket):
        if IS_DEBUG:
            print(f"socket_update {self.bl_idname}")

    def socket_value_update(self, context):
        if IS_DEBUG:
            print(f"socker_value_update {self.bl_idname}")

    def update_obm(self):
        if IS_DEBUG:
            print(f"update_obm {self.bl_idname}")


class ObmConstantNode(ObmSoundNode, NodeCustomGroup):
    def socket_update(self, socket):
        super().socket_update(socket)
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value
            link.to_node.update_obm()


class ObjectNode(ObmConstantNode):
    '''Object Node'''
    bl_idname = 'ObmObjectNodeType'
    bl_label = "Object"

    def init(self, context):
        object_socket = self.outputs.new('ObjectSocketType', "Object")
        print(object_socket.is_constant)
        object_socket.is_constant = True
        print(object_socket.is_constant)
        print(self.outputs[0].is_constant)
        self.outputs[0].is_constant = True
        print(self.outputs[0].is_constant)

class FloatNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmFloatNodeType'
    bl_label = "Value"

    def init(self, context):
        float_socket = self.outputs.new('FloatSocketType', "Float")
        float_socket.is_constant = True

class IntNode(ObmConstantNode):
    '''Value Node'''
    bl_idname = 'ObmIntNodeType'
    bl_label = "Integer"

    def init(self, context):
        int_socket = self.outputs.new('IntSocketType', "Integer")
        int_socket.is_constant = True

class StringNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmStringNodeType'
    bl_label = "String"

    def init(self, context):
        string_socket = self.outputs.new('StringSocketType', "String")
        string_socket.is_constant = True

class BooleanNode(ObmConstantNode):
    '''Boolean Value Node'''
    bl_idname = 'ObmBooleanNodeType'
    bl_label = "Boolean"

    def init(self, context):
        bool_socket = self.outputs.new('BoolSocketType', "Boolean")
        bool_socket.is_constant = True