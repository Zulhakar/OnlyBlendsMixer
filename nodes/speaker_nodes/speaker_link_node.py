import bpy

from ...config import IS_DEBUG
from ..mixer_node import ObmSoundNode
from ...base.helper import get_length_and_specs_from_sound


def calculation_of_length(sound):
    length, specs = get_length_and_specs_from_sound(sound)
    sample_rate, channels = specs
    sound_length_sec = length / sample_rate
    fps = bpy.context.scene.render.fps
    strip_frame_length = int(sound_length_sec * fps)
    return strip_frame_length


class SpeakerLinkNode(ObmSoundNode, bpy.types.Node):
    '''Speaker Link Node to assign a Sound to a Speaker'''
    bl_label = "Speaker Link"
    bl_icon = 'OUTLINER_DATA_SPEAKER'

    def init(self, context):
        self.inputs.new('NodeSocketSpeaker', "Speaker")
        self.inputs.new('NodeSocketSound', "Sound")
        super().init(context)

    def free(self):
        super().free()
        speaker = self.inputs[0].input_value
        sound = self.inputs[1].input_value
        if speaker is not None and sound is not None:
            if speaker.sound is not None:
                if speaker.sound.name == sound.name:
                    speaker.sound = None

    def link_sound_and_speaker(self):
        speaker = self.inputs[0].input_value
        sound = self.inputs[1].input_value
        if speaker is not None and sound is not None and speaker.name in bpy.data.objects:
            speaker.sound = sound
            speaker.animation_data_create()
            action_name = f"{speaker.name}_action"
            if action_name in bpy.data.actions:
                bpy.data.actions.remove(bpy.data.actions[action_name])
            action = bpy.data.actions.new(action_name)

            speaker.animation_data.action = action
            strip_name = f"{speaker.name}_Strip"
            #if strip_name not in bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips and len(bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips) <= 0:
            #    strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips.new(strip_name, 0, action)
            #else:
            strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips[0]
            try:
                strip_frame_length = calculation_of_length(sound)
                strip.name = f"{speaker.name}_Strip"
                strip.frame_end = strip.frame_start + strip_frame_length
            except Exception as e:
                if IS_DEBUG:
                    print(e)
        else:
            if self.inputs[1].input_value is None:
                if speaker:
                    action_name = f"{speaker.name}_action"
                    if action_name in bpy.data.actions:
                        bpy.data.actions.remove(bpy.data.actions[action_name])
                    strip_name = f"{speaker.name}_Strip"
                    if strip_name in bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips:
                        strip_to_remove = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips[strip_name]
                        strip_to_remove.frame_end = 0.0
                        #bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips.remove(strip_to_remove)
                    #for strip in bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"]:
                    #    if strip_name == strip.name:
                    #        bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].remove(strip)
                    #        break
            if speaker and speaker.name not in bpy.data.objects:
                self.inputs[0].input_value = None
    def socket_update(self, socket):
        super().socket_update(socket)
        self.link_sound_and_speaker()
