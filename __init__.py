import bpy
from .properties import SoundSampleCollection, GatewayCollection, GroupOutputCollection
from .obm_node_editor import register as register_obm_nodes
from .obm_node_editor import unregister as unregister_obm_nodes
from .sockets.basic_sockets import register as register_basic_sockets
from .sockets.basic_sockets import unregister as unregister_basic_sockets
from .helper import play_sample
from .global_data import Data
from bpy.app.handlers import persistent
from .properties import on_depsgraph_update

current_frame = 0


@persistent
def frame_change_update(scene, graph):
    global current_frame
    frame = bpy.context.scene.frame_current
    # print(bpy.context.scene.samples)
    if current_frame != frame:

        if bpy.context.scene.samples is not None and len(bpy.context.scene.samples) > 0:
            for sound_sample in bpy.context.scene.samples:
                if sound_sample.is_played:
                    print("frame_change_update")
                    # play_selection(bpy.data.objects[sound_sample.linked_object_name])
                    if sound_sample.sample_uuid in Data.geometry_to_sample_nodes:
                        print("update geometry sound node")
                        sound_geometry_node = Data.geometry_to_sample_nodes[sound_sample.sample_uuid]
                        sound_geometry_node.operation_update()

                    sound = Data.uuid_data_storage[sound_sample.sample_uuid]
                    device = Data.uuid_data_storage[sound_sample.device_uuid]
                    play_sample(device, sound)

    current_frame = frame


@persistent
def load_blend_file_job(file_name):
    # print(bpy.data.node_groups)
    for group in bpy.data.node_groups:
        # print(group.name)
        for node in group.nodes:
            # print(node.name)
            if hasattr(node, "refresh_outputs"):
                print(node.name)
                try:
                    node.refresh_outputs()
                except Exception as e:
                    print(e)
        for node in group.nodes:
            # print(node.name)
            if hasattr(node, "refresh_outputs"):
                print(node.name)
                try:
                    node.refresh_outputs()
                except Exception as e:
                    print(e)


# reg_classes = ui_classes
# reg_classes.extend([ SoundSampleCollection])

class_register, class_unregister = bpy.utils.register_classes_factory([SoundSampleCollection, GatewayCollection,
                                                                       GroupOutputCollection])


# bpy.ops.workspace.append_activate(
#     idname='SoundNodes',  # Name of the workspace to import
#     filepath='startup.blend'
# )
def register():
    register_obm_nodes()
    register_basic_sockets()
    class_register()
    bpy.types.Scene.samples = bpy.props.CollectionProperty(type=SoundSampleCollection)
    bpy.types.Scene.obm_gateways = bpy.props.CollectionProperty(type=GatewayCollection)

    bpy.types.Scene.geometry_to_sample_nodes_num = bpy.props.IntProperty(default=0)
    bpy.types.Scene.group_collection_prop = bpy.props.CollectionProperty(type=GroupOutputCollection)

    # bpy.app.timers.register(record_iteration, first_interval=0.0)
    bpy.app.handlers.frame_change_post.append(frame_change_update)
    bpy.app.handlers.load_post.append(load_blend_file_job)


def unregister():
    unregister_obm_nodes()
    unregister_basic_sockets()
    class_unregister()

    del bpy.types.Scene.samples
    del bpy.types.Scene.obm_gateways
    del bpy.types.Scene.geometry_to_sample_nodes_num
    del bpy.types.Scene.group_collection_prop

    bpy.app.handlers.frame_change_post.remove(frame_change_update)
    bpy.app.handlers.load_post.remove(load_blend_file_job)
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)


if __name__ == "__main__":
    register()
