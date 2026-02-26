import bpy
from ..config import IS_DEBUG, VERSATILE_SOCKET_SHAPE, SINGLE_VALUES_SOCKET_SHAPE, OB_TREE_TYPE
from ..base.helper import get_node_id_name
from ..base.global_data import Data


class ObmSoundNode:
    socket_update_disabled: bpy.props.BoolProperty(default=False)

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
            self.node_uuid = get_node_id_name(self)
            Data.uuid_data_storage[self.node_uuid] = None

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == OB_TREE_TYPE

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


class ObmSampleNode(ObmSoundNode, bpy.types.Node):
    '''Sample Node'''
    bl_icon = 'SEQ_HISTOGRAM'
    node_uuid: bpy.props.StringProperty()
