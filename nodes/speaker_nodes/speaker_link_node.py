import bpy
from ...nodes.basic_nodes import ObmConstantNode
from ...aud_helper import get_length_and_specs_from_sound
from ...constants import IS_DEBUG


def bad_calculation_of_length(sound):
    # stupid and expensive...
    length, specs = get_length_and_specs_from_sound(sound)
    sample_rate, channels = specs
    sound_length_sec = length / sample_rate
    fps = bpy.context.scene.render.fps
    strip_frame_length = int(sound_length_sec * fps)
    return strip_frame_length


class SpeakerLinkNode(ObmConstantNode):
    '''Speaker Node'''
    bl_idname = 'SpeakerLinkNodeType'
    bl_label = "Speaker Link"
    bl_icon = 'OUTLINER_DATA_SPEAKER'
    def init(self, context):
        self.inputs.new('SpeakerSocketType', "Speaker")
        self.inputs.new('SoundSocketType', "Sound")
        self.inputs.new('FloatSocketType', "Volume")
        super().init(context)

    def free(self):
        #unlink sound, maybe not necessary or 'problematic'
        super().free()
        speaker = self.inputs[0].input_value
        sound = self.inputs[1].input_value
        if speaker is not None and sound is not None:
            if speaker.sound is not None:
                if speaker.sound.name == sound.name:
                    speaker.sound = None

    def link_sound_and_speaker(self):
        if len(self.inputs) > 2:
            if hasattr(self.inputs[0], 'input_value') and hasattr(self.inputs[1], 'input_value'):
                speaker = self.inputs[0].input_value
                sound = self.inputs[1].input_value
                if speaker is not None and sound is not None:
                    speaker.sound = sound
                    speaker.animation_data_create()
                    action_name = f"{speaker.name}_action"
                    if action_name in bpy.data.actions:
                        bpy.data.actions.remove(bpy.data.actions[action_name])
                    action = bpy.data.actions.new(action_name)

                    speaker.animation_data.action = action
                    strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips[0]
                    strip_frame_length = bad_calculation_of_length(sound)
                    strip.name = f"{speaker.name}_Strip"
                    strip.frame_end = strip.frame_start + strip_frame_length
                else:
                    print("speaker or sound is None")
                    print(speaker)
                    print(sound)
        else:
            print(str(len(self.inputs)))

    def update(self):
        super().update()
        self.link_sound_and_speaker()

    def update_obm(self):
        self.link_sound_and_speaker()

    def insert_link(self, link):
        super().insert_link(link)
        if link.is_valid:
            if link.to_socket == self.inputs[1]:
                self.inputs[1].input_value = link.from_socket.input_value
            self.link_sound_and_speaker()
        else:
            print(link.is_valid)

    def socket_update(self, socket):
        if IS_DEBUG:
            print(f"socket_update {self.bl_idname}")
        self.link_sound_and_speaker()
