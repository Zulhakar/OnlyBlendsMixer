import bpy
from .properties import  SoundSampleCollection, GatewayCollection
from .custom_node_test import register as reg3
from .custom_node_test import unregister as unreg3
from .basic_sockets import register as register_basic_sockets
from .basic_sockets import unregister as unregister_basic_sockets
from .helper import play_selection, play_sample, stop_play
from .global_data import Data
from bpy.app.handlers import persistent

current_frame = 0

@persistent
def frame_change_update(scene, graph):
    global current_frame
    frame = bpy.context.scene.frame_current
    #print(bpy.context.scene.samples)
    if current_frame != frame:

        if bpy.context.scene.samples is not None and len(bpy.context.scene.samples) > 0:
            for sound_sample in bpy.context.scene.samples:
                if sound_sample.is_played:
                    print("frame_change_update")
                    #play_selection(bpy.data.objects[sound_sample.linked_object_name])
                    sound = Data.uuid_data_storage[sound_sample.sample_uuid]
                    device = Data.uuid_data_storage[sound_sample.device_uuid]
                    play_sample(device, sound)

    current_frame = frame

@persistent
def load_blend_file_job(file_name):
    print(bpy.data.node_groups)
    for group in bpy.data.node_groups:
        print(group.name)
        for node in group.nodes:
            print(node.name)
            if hasattr(node, "refresh_outputs"):
                try:
                    node.refresh_outputs()
                except Exception as e:
                    print(e)
        for node in group.nodes:
            print(node.name)
            if hasattr(node, "refresh_outputs"):
                try:
                    node.refresh_outputs()
                except Exception as e:
                    print(e)


#reg_classes = ui_classes
#reg_classes.extend([ SoundSampleCollection])

class_register, class_unregister = bpy.utils.register_classes_factory([ SoundSampleCollection, GatewayCollection])


def register():
    reg3()
    register_basic_sockets()
    class_register()
    bpy.types.Scene.samples = bpy.props.CollectionProperty(type=SoundSampleCollection)
    bpy.types.Scene.obm_gateways = bpy.props.CollectionProperty(type=GatewayCollection)
    #bpy.app.timers.register(record_iteration, first_interval=0.0)
    bpy.app.handlers.frame_change_post.append(frame_change_update)
    bpy.app.handlers.load_post.append(load_blend_file_job)

def unregister():
    unreg3()
    unregister_basic_sockets()
    class_unregister()
    del bpy.types.Scene.samples
    del bpy.types.Scene.obm_gateways
    bpy.app.handlers.frame_change_post.remove(frame_change_update)
    bpy.app.handlers.load_post.remove(load_blend_file_job)

if __name__ == "__main__":
    register()
