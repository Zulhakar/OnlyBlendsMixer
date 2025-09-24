import bpy
from bpy.types import NodeCustomGroup
from .constants import IS_DEBUG


class ObmSoundNode:

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

    def update(self):
        if IS_DEBUG:
            print(f"update {self.bl_idname}")

    def socket_update(self, socket):
        if IS_DEBUG:
            print(f"socket_update {self.bl_idname}")

    def update_obm(self):
        if IS_DEBUG:
            print(f"update_obm {self.bl_idname}")


class ObmConstantNode(ObmSoundNode, NodeCustomGroup):
    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            self.outputs[0].input_value = socket.input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
                if hasattr(link.to_node, "update_obm"):
                    link.to_node.update_obm()


class ObjectNode(ObmConstantNode):
    '''Object Node'''
    bl_idname = 'ObmObjectNodeType'
    bl_label = "Object"

    def init(self, context):
        self.outputs.new('ObjectSocketConstantType', "Object")


class FloatNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmFloatNodeType'
    bl_label = "Value"

    def init(self, context):
        self.outputs.new('FloatSocketConstantType', "Float")


class IntNode(ObmConstantNode):
    '''Value Node'''
    bl_idname = 'ObmIntNodeType'
    bl_label = "Integer"

    def init(self, context):
        self.outputs.new('IntSocketConstantType', "Integer")


class StringNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmStringNodeType'
    bl_label = "String"

    def init(self, context):
        self.outputs.new('StringSocketConstantType', "String")


class BooleanNode(ObmConstantNode):
    '''Boolean Value Node'''
    bl_idname = 'ObmBooleanNodeType'
    bl_label = "Boolean"

    def init(self, context):
        self.outputs.new('BoolSocketConstantType', "Boolean")
