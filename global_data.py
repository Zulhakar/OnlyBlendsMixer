import bpy
from bpy_extras.io_utils import ImportHelper
from .constants import FILE_IMPORT_OT_ID

def create_dynamic_import_wav_op(parent, node_uuid):
    class_name = FILE_IMPORT_OT_ID + "_" + node_uuid
    def execute(self, context):
        print("Import WAV:", self.filepath)
        self.parent.import_path = self.filepath

        #print(self)
        #print(context)
        return {'FINISHED'}

    DynamicImportWavOperatorClass = type(class_name, (bpy.types.Operator,  ImportHelper), {
        "bl_label": FILE_IMPORT_OT_ID,
        "bl_idname": class_name,
        "node_uuid": node_uuid,
        "parent": parent,
        "execute": execute,
    })
    return DynamicImportWavOperatorClass


class Data:
    persistent_data = []
    channel = None
    buf = 256
    sound_node = {}

    uuid_data_storage = {}
    uuid_operator_class_storage = {}
    uuid_node_socket_storage = {}
    uuid_geometry_data_storage = {}
    geometry_sound_nodes = {}
    @classmethod
    def create_import_wave_panel(cls, parent, node_uuid):
        op_class = create_dynamic_import_wav_op(parent, node_uuid)
        cls.uuid_operator_class_storage[node_uuid] = op_class
        bpy.utils.register_class(op_class)
