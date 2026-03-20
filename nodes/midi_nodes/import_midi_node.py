import bpy
from bpy_extras.io_utils import ImportHelper

import uuid
from ..mixer_node import ObmSoundNode
from ...base.helper import get_node_id_name
from ...config import IS_DEBUG
from ...cnt.base.global_data import Data


class ImportObc(bpy.types.Operator, ImportHelper):
    """Import a file"""

    bl_label = "Import"

    # filename_ext = ".mid"

    filter_glob: bpy.props.StringProperty(
        default="*.midi;*.mid;*.smf",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        self.parent.import_path = self.filepath
        return {'FINISHED'}


def create_dynamic_import_op(parent, node_uuid):
    class_name = f'obc_import_ot_id.{node_uuid}'
    DynamicImportOperatorClass = type(class_name, (ImportObc,), {
        "bl_idname": class_name,
        "node_uuid": node_uuid,
        "parent": parent,

    })

    return DynamicImportOperatorClass

def create_import_panel(parent, node_uuid):
    op_class = create_dynamic_import_op(parent, node_uuid)
    bpy.utils.register_class(op_class)
    Data.uuid_operator_class_storage[node_uuid] = op_class

class ImportMidiNode(ObmSoundNode, bpy.types.Node):
    bl_label = "Import MIDI"
    import_path: bpy.props.StringProperty(update=lambda self, context: self.__update_import_path())
    node_uuid: bpy.props.StringProperty()

    bl_icon = 'EXTERNAL_DRIVE'

    def init(self, context):

        self.inputs.new("NodeSocketImportObc", "Path")
        self.outputs.new('NodeSocketMidi', "MIDI")
        super().init(context)
        self.node_uuid = str(uuid.uuid4()).replace("-", "")
        create_import_panel(self, self.node_uuid)

    def free(self):
        if self.node_uuid in Data.uuid_operator_class_storage:
            bpy.utils.unregister_class(Data.uuid_operator_class_storage[self.node_uuid])

    def __update_import_path(self):
        self.inputs[0].input_value = self.import_path
        self.outputs[0].input_value = self.import_path

    def refresh(self):
        if IS_DEBUG:
            self.log("refresh")
        create_import_panel(self, self.node_uuid)

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket.is_output:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value
