import bpy
import aud
import uuid
from ..constants import IS_DEBUG, SINGLE_VALUES_SOCKET_SHAPE, VERSATILE_SOCKET_SHAPE
from ..constants import SOUND_TREE_TYPE
from ..global_data import Data
from functools import wraps


class ObmSoundNode:

    def log(self, func_name):
        if IS_DEBUG:
            log_string = f"{self.bl_idname}-> {self.name}: {func_name} was called"
            print(log_string)

    def init(self, context):
        self.sound_data_init()

        for output in self.outputs:
            if not output.is_multi_input:
                if bpy.app.version < (5, 0, 1):
                    output.display_shape = VERSATILE_SOCKET_SHAPE
                else:
                    output.display_shape = SINGLE_VALUES_SOCKET_SHAPE
        for input in self.inputs:
            if not input.is_multi_input:
                if bpy.app.version < (5, 0, 1):
                    input.display_shape = VERSATILE_SOCKET_SHAPE
                else:
                    input.display_shape = SINGLE_VALUES_SOCKET_SHAPE

    def sound_data_init(self):
        if hasattr(self, "node_uuid"):
            uuid_tmp = str(uuid.uuid4()).replace("-", "")
            self.node_uuid = uuid_tmp
            self.outputs[0].input_value = uuid_tmp
            Data.uuid_data_storage[uuid_tmp] = None

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == SOUND_TREE_TYPE

    def copy(self, node):
        self.log("copy")
        self.sound_data_init()

    def free(self):
        self.log("free")
        if hasattr(self, "node_uuid"):
            if self.node_uuid in Data.uuid_data_storage.keys():
                del Data.uuid_data_storage[self.node_uuid]
                if IS_DEBUG:
                    print(f"{self.node_uuid} data deleted")

    def refresh_outputs(self):
        self.log("refresh")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        self.log("insert_link")
        if link.to_socket.bl_idname != link.from_socket.bl_idname:
            # self.error_message_set("Falscher Socket-Typ!")
            if IS_DEBUG:
                print("Wrong Socket ", str(link.from_socket.bl_idname))
            link.is_valid = False
        else:
            link.is_valid = True
        if link.is_valid and not self.mute:
            for input in self.inputs:
                if link.to_socket == input:
                    if link.to_socket.is_multi_input:
                        pass
                    else:
                        if link.to_socket.bl_idname == "FloatVectorFieldSocketType":
                            input.input_value.clear()
                            for item in link.from_socket.input_value:
                                new_item = input.input_value.add()
                                new_item.value = item.value
                        else:
                            input.input_value = link.from_socket.input_value
                        self.state_update()
        else:
            pass

    def update(self):
        self.log("update")

    def socket_update(self, socket):
        self.log("socket_update")

    def socket_value_update(self, context):
        self.log("socket_value_update")

    def update_obm(self):
        self.log("update_obm")

    def state_update(self):
        self.log("state_update")


class ObmSampleNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Sample Node'''
    bl_icon = 'SEQ_HISTOGRAM'
    def refresh_outputs(self):
        super().refresh_outputs()
        self.state_update()

    def update(self):
        # This method is called when the node updates
        super().update()
        if len(self.outputs) > 0:
            if self.mute:
                self.outputs[0].input_value = ""
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
                    if hasattr(link.to_node, "update_obm"):
                        link.to_node.update_obm()
            else:
                self.outputs[0].input_value = self.node_uuid
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
                    if hasattr(link.to_node, "update_obm"):
                        link.to_node.update_obm()
                self.update_obm()

    def update_obm(self):
        super().update_obm()
        self.state_update()
        for link in self.outputs[0].links:
            # link.to_node.update_obm(self, self.outputs[0])
            if hasattr(link.to_node, "update_obm"):
                link.to_node.update_obm()

    def socket_update(self, socket):
        if not self.mute:
            super().socket_update(socket)
            if not socket.is_output:
                self.state_update()
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
                    #link.to_node.update_obm()


class ObmConstantNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    def socket_update(self, socket):
        super().socket_update(socket)
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value
            #link.to_node.update_obm()


class ObjectNode(ObmConstantNode):
    '''Object Node'''
    bl_idname = 'ObmObjectNodeType'
    bl_label = "Object"

    def init(self, context):
        object_socket = self.outputs.new('ObjectSocketType', "Object")
        object_socket.is_constant = True
        super().init(context)


class FloatNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmFloatNodeType'
    bl_label = "Value"

    def init(self, context):
        float_socket = self.outputs.new('FloatSocketType', "Float")
        float_socket.is_constant = True
        super().init(context)


class IntNode(ObmConstantNode):
    '''Value Node'''
    bl_idname = 'ObmIntNodeType'
    bl_label = "Integer"

    def init(self, context):
        int_socket = self.outputs.new('IntSocketType', "Integer")
        int_socket.is_constant = True
        super().init(context)


class StringNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmStringNodeType'
    bl_label = "String"

    def init(self, context):
        string_socket = self.outputs.new('StringSocketType', "String")
        string_socket.is_constant = True
        super().init(context)


class BooleanNode(ObmConstantNode):
    '''Boolean Value Node'''
    bl_idname = 'ObmBooleanNodeType'
    bl_label = "Boolean"

    def init(self, context):
        bool_socket = self.outputs.new('BoolSocketType', "Boolean")
        bool_socket.is_constant = True
        super().init(context)
