import bpy
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper
from .constants import FILE_IMPORT_OT_ID, IS_DEBUG


def on_mesh_update(obj, scene):
    if IS_DEBUG:
        print("mesh update")
    for node_key in Data.geometry_to_sample_nodes:
        node = Data.geometry_to_sample_nodes[node_key]
        if obj.name and node.obj and node.obj.name == obj.name:
            node.state_update(None)


@persistent
def on_depsgraph_update(scene):
    if IS_DEBUG:
        print("depsgraph update")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.Object):
            if update.is_updated_geometry:
                on_mesh_update(update.id, scene)



@persistent
def load_blend_file_job(file_name):
    bpy.context.scene.geometry_to_sample_nodes_num = 0
    for group in bpy.data.node_groups:
        for node in group.nodes:
            if hasattr(node, "refresh_outputs"):
                node.refresh_outputs()

def create_dynamic_import_wav_op(parent, node_uuid):
    class_name = FILE_IMPORT_OT_ID + "_" + node_uuid
    def execute(self, context):
        if IS_DEBUG:
            print("Import WAV:", self.filepath)
        self.parent.import_path = self.filepath
        # print(self)
        # print(context)
        return {'FINISHED'}

    DynamicImportWavOperatorClass = type(class_name, (bpy.types.Operator, ImportHelper), {
        "bl_label": FILE_IMPORT_OT_ID,
        "bl_idname": class_name,
        "node_uuid": node_uuid,
        "parent": parent,
        "execute": execute,
    })
    return DynamicImportWavOperatorClass


class Data:
    uuid_data_storage = {}
    uuid_operator_class_storage = {}
    uuid_node_socket_storage = {}
    uuid_geometry_data_storage = {}
    geometry_to_sample_nodes = {}

    @classmethod
    def create_import_wave_panel(cls, parent, node_uuid):
        op_class = create_dynamic_import_wav_op(parent, node_uuid)
        cls.uuid_operator_class_storage[node_uuid] = op_class
        bpy.utils.register_class(op_class)
