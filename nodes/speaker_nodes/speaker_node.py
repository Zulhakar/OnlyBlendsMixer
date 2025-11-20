from ...nodes.basic_nodes import ObmConstantNode
from ...sockets.basic_sockets import SoundSocket
import bpy
from ...aud_helper import get_length_and_specs_from_sound

def bad_calculation_of_length(sound):
    # stupid and expensive...
    length, specs = get_length_and_specs_from_sound(sound)
    sample_rate, channels = specs
    sound_length_sec = length / sample_rate
    print(sound_length_sec)
    fps = bpy.context.scene.render.fps
    strip_frame_length = int(sound_length_sec * fps)
    return strip_frame_length

class SpeakerNode(ObmConstantNode):
    '''Speaker Node'''
    bl_idname = 'SpeakerNodeType'
    bl_label = "Speaker"

    def init(self, context):
        self.outputs.new('SpeakerSocketType', "Speaker")
        self.inputs.new('SoundSocketType', "Sound")
        self.inputs.new('FloatSocketType', "Volume")
        self.outputs.new('FloatSocketType', "V2")

        super().init(context)

    def socket_update(self, socket):
        super().socket_update(socket)
        speaker = self.outputs[0].input_value
        sound = self.inputs[0].input_value
        if socket == self.inputs[0]:
            if isinstance(socket, SoundSocket):
                print("Sound Socket Changed")
                speaker.sound = sound
                speaker.animation_data_create()
                action = bpy.data.actions.new("SpeakerAction")
                speaker.animation_data.action = action

                strip = bpy.data.objects[speaker.name].animation_data.nla_tracks["SoundTrack"].strips["NLA Strip"]
                strip_frame_length = bad_calculation_of_length(sound)
                strip.frame_end = strip.frame_start + strip_frame_length

    def update_obm(self):
        super().update_obm()
