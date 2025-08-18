import os
import bpy
from .helper import record



def get_link_object_name(self):
    return self["testprop"]


def set_link_object_name(self, value):
    self["testprop"] = value


class SoundSampleCollection(bpy.types.PropertyGroup):
    node_uuid: bpy.props.StringProperty()
    #is_played: bpy.props.BoolProperty(update=lambda self, context: self.play_function2( context))
    is_played: bpy.props.BoolProperty(default=False)
    sample_uuid: bpy.props.StringProperty()
    device_uuid: bpy.props.StringProperty()

class GatewayCollection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    socket_num :  bpy.props.IntProperty()

def start_animation(self, context):
    bpy.ops.screen.animation_play()


def stop_animation(self, context):
    bpy.ops.screen.animation_cancel()
    context.scene.frame_set(0)
    global persistent_data
    if len(persistent_data) > 0:
        print(bpy.types.Scene.mixer_props)
        save_array_to_wave(context.scene.mixer_props.record_file_path, persistent_data)
    persistent_data = []



def record_iteration():
    """
    The main loop function that gets called repeatedly
    Returns the interval for next call, or None to stop
    """
    scene = bpy.context.scene
    mixer_loop_props = scene.mixer_props

    # Check if loop should continue
    if not mixer_loop_props.enable_mixer_loop:
        return None  # Stop

    mixer_loop_props.iteration_count += 1

    # this runs on the main thread !!!
    duration = record()

    mixer_loop_props.play_duration = duration
    # Force UI update
    for area in bpy.context.screen.areas:
        if area.type in ['VIEW_3D', 'PROPERTIES']:
            area.tag_redraw()

    return mixer_loop_props.play_duration - (Data.buf / 44100)
