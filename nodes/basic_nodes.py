import bpy
import aud
import uuid
from ..core.constants import IS_DEBUG, SINGLE_VALUES_SOCKET_SHAPE, VERSATILE_SOCKET_SHAPE
from ..core.constants import SOUND_TREE_TYPE
from ..core.global_data import Data


class ObmSoundNode:
    socket_update_disabled : bpy.props.BoolProperty(default=False)
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
                        if link.to_socket.bl_idname != "FloatVectorFieldSocketType":
                            input.input_value = link.from_socket.input_value
                            # input.input_value.clear()
                            # for item in link.from_socket.input_value:
                            #     new_item = input.input_value.add()
                            #     new_item.value = item.value
                            #     print(str(new_item.value[0]))
                            # print("sock update")
                            # link.to_node.socket_update(link.to_socket)
                        # else:
                        #     input.input_value = link.from_socket.input_value
                        #     print(f"input_value: {input.input_value}")
        else:
            pass

    def update(self):
        self.log("update")

    def socket_update(self, socket):
        self.log("socket_update")
        if IS_DEBUG:
            if self.socket_update_disabled:
                print("socket_update_disabled")
    def socket_value_update(self, context):
        self.log("socket_value_update")



class ObmSampleNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Sample Node'''
    bl_icon = 'SEQ_HISTOGRAM'
    node_uuid: bpy.props.StringProperty()


class ObmConstantNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    def socket_update(self, socket):
        super().socket_update(socket)
        if not self.socket_update_disabled:
            if len(self.outputs) > 0:
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value



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
    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.outputs[0].input_value = node.outputs[0].input_value
        self.socket_update_disabled = False


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
