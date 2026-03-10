import bpy
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper
from ..config import IS_DEBUG, MIDI_IMPORT_OT_ID


def __on_mesh_update(obj, scene):
    if IS_DEBUG:
        print("mesh update")
    for node_key in Data.geometry_to_sample_nodes:
        node = Data.geometry_to_sample_nodes[node_key]
        if obj.name and node.obj and node.obj.name == obj.name:
            node.state_update(None)


@persistent
def __on_depsgraph_update(scene):
    if IS_DEBUG:
        print("depsgraph update")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.Object):
            if update.is_updated_geometry:
                __on_mesh_update(update.id, scene)


def __add_depsgraph_handler():
    bpy.context.scene.geometry_to_sample_nodes_num = 0
    if __on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(__on_depsgraph_update)


def __refresh_nodes():
    for group in bpy.data.node_groups:
        for node in group.nodes:
            if hasattr(node, "refresh_outputs"):
                node.refresh_outputs()


@persistent
def load_blend_file_job(file_name):
    # add_depsgraph_handler()
    __refresh_nodes()


class ImportMidi(bpy.types.Operator, ImportHelper):
    """Import a MIDI file"""

    bl_label = "Import MIDI"

    # ImportHelper mix-in class uses this.
    filename_ext = ".mid"

    filter_glob: bpy.props.StringProperty(
        default="*.midi;*.mid;*.smf",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        if IS_DEBUG:
            print("Import MIDI:", self.filepath)
        self.parent.import_path = self.filepath
        return {'FINISHED'}


def create_dynamic_import_midi_op(parent, node_uuid):
    class_name = MIDI_IMPORT_OT_ID + "." + node_uuid

    DynamicImportMidiOperatorClass = type(class_name, (ImportMidi,), {
        "bl_idname": class_name,
        "node_uuid": node_uuid,
        "parent": parent,

    })

    return DynamicImportMidiOperatorClass


class Data:
    uuid_data_storage = {}
    # for import midi node
    uuid_operator_class_storage = {}

    @classmethod
    def create_midi_import_panel(cls, parent, node_uuid):
        op_class = create_dynamic_import_midi_op(parent, node_uuid)
        bpy.utils.register_class(op_class)
        Data.uuid_operator_class_storage[node_uuid] = op_class
