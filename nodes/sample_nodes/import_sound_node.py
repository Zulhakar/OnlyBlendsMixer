import bpy
from bpy_extras.io_utils import ImportHelper

import uuid
from ..mixer_node import ObmSoundNode
from ...config import IS_DEBUG
from ...cnt.base.global_data import Data


class ImportSoundObm(bpy.types.Operator, ImportHelper):
    """Import a file"""

    bl_label = "Import"

    # filename_ext = ".mid"

    filter_glob: bpy.props.StringProperty(
        default="*.wav;*.mp3;*.flac",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        self.parent.import_path = self.filepath
        return {'FINISHED'}


def create_dynamic_import_op(parent, node_uuid):
    class_name = f'obm_import_sound_ot_id.{node_uuid}'
    DynamicImportOperatorClass = type(class_name, (ImportSoundObm,), {
        "bl_idname": class_name,
        "node_uuid": node_uuid,
        "parent": parent,

    })

    return DynamicImportOperatorClass

def create_import_panel(parent, node_uuid):
    op_class = create_dynamic_import_op(parent, node_uuid)
    bpy.utils.register_class(op_class)
    Data.uuid_operator_class_storage[node_uuid] = op_class

class ImportSoundNodeObm(ObmSoundNode, bpy.types.Node):
    bl_label = "Import Sound"
    import_path: bpy.props.StringProperty(update=lambda self, context: self.__update_import_path())
    node_uuid: bpy.props.StringProperty()

    bl_icon = 'FILE_SOUND'

    def init(self, context):

        self.inputs.new("NodeSocketImportObc", "Path")
        self.outputs.new('NodeSocketSoundObm', "Sound")
        super().init(context)
        self.node_uuid = str(uuid.uuid4()).replace("-", "")
        create_import_panel(self, self.node_uuid)

    def free(self):
        if self.node_uuid in Data.uuid_operator_class_storage:
            bpy.utils.unregister_class(Data.uuid_operator_class_storage[self.node_uuid])

    def __update_import_path(self):
        self.inputs[0].input_value = self.import_path
        try:
            new_data = bpy.data.sounds.load(self.import_path, check_existing=True)
            self.outputs[0].input_value = new_data
        except Exception as e:
            print(e)

    def refresh(self):
        if IS_DEBUG:
            self.log("refresh")
        create_import_panel(self, self.node_uuid)

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket.is_output:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value
        else:
            try:
                new_data = bpy.data.sounds.load(socket.input_value, check_existing=True)
                self.outputs[0].input_value = new_data
            except Exception as e:
                print(e)