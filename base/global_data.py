import bpy
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper
from ..config import IS_DEBUG

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
    #add_depsgraph_handler()
    __refresh_nodes()

class Data:
    uuid_data_storage = {}
