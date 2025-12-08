import bpy
from .obm_node_editor import register as register_obm_nodes
from .obm_node_editor import unregister as unregister_obm_nodes
from .sockets.basic_sockets import register as register_basic_sockets
from .sockets.basic_sockets import unregister as unregister_basic_sockets
from .core.global_data import Data
from .core.global_data import load_blend_file_job, on_depsgraph_update


def register():
    register_obm_nodes()
    register_basic_sockets()
    #class_register()
    #bpy.types.Scene.samples = bpy.props.CollectionProperty(type=SoundSampleCollection)

    bpy.types.Scene.geometry_to_sample_nodes_num = bpy.props.IntProperty(default=0)
    #bpy.types.Scene.group_collection_prop = bpy.props.CollectionProperty(type=GroupOutputCollection)

    # bpy.app.timers.register(record_iteration, first_interval=0.0)
    bpy.app.handlers.load_post.append(load_blend_file_job)

    #bpy.app.timers.register(sound_nodes_workspace.register, first_interval=10.0)
    #sound_nodes_workspace.register()

def unregister():
    unregister_obm_nodes()
    unregister_basic_sockets()
    #class_unregister()

    #del bpy.types.Scene.samples
    del bpy.types.Scene.geometry_to_sample_nodes_num
    #del bpy.types.Scene.group_collection_prop

    bpy.app.handlers.load_post.remove(load_blend_file_job)
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

if __name__ == "__main__":
    register()
