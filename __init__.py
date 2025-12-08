import bpy
from bpy.utils import register_class
from bpy.utils import unregister_class
from .sockets.basic_sockets import register as register_basic_sockets
from .sockets.basic_sockets import unregister as unregister_basic_sockets
from .node_editor import register as register_node_editor
from .node_editor import unregister as unregister_node_editor
from .core.global_data import load_blend_file_job, on_depsgraph_update
from .nodes import classes as nodes_classes

def register():
    for node_class in nodes_classes:
        register_class(node_class)
    register_basic_sockets()
    register_node_editor()
    bpy.types.Scene.geometry_to_sample_nodes_num = bpy.props.IntProperty(default=0)
    bpy.app.handlers.load_post.append(load_blend_file_job)

def unregister():
    for node_class in reversed(nodes_classes):
        unregister_class(node_class)

    unregister_basic_sockets()
    unregister_node_editor()

    del bpy.types.Scene.geometry_to_sample_nodes_num

    bpy.app.handlers.load_post.remove(load_blend_file_job)
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

if __name__ == "__main__":
    register()
