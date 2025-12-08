import bpy
import mathutils
from bpy_extras.io_utils import ImportHelper

from .core.helper import play_selection
from .core.constants import *

class PLAY_OT(bpy.types.Operator):
    bl_label = PLAY_OT_label
    bl_idname = PLAY_OT_ID

    def execute(self, context):
        obj_name = self.properties["object_name"]
        print("play:", obj_name)
        play_selection(bpy.data.objects[obj_name])
        return {"FINISHED"}


class FILE_SELECT_OT_rec(bpy.types.Operator, ImportHelper):
    bl_idname = FILE_REC_OT_ID
    bl_label = FILE_REC_OT_label

    filename_ext = ".wav"

    filter_glob: bpy.props.StringProperty(
        default="*.wav"
    )

    def execute(self, context):
        context.scene.mixer_props.record_file_path = self.filepath
        print("NAME:", context.scene.mixer_props.record_file_path)
        return {'FINISHED'}


class FILE_SELECT_OT_import_wav(bpy.types.Operator, ImportHelper):
    bl_idname = FILE_IMPORT_OT_ID
    bl_label = FILE_IMPORT_OT_label

    filename_ext = ".wav"

    filter_glob: bpy.props.StringProperty(
        default="*.wav",
    )

    def execute(self, context):
        context.scene.mixer_props.import_wav_file_path = self.filepath
        print("Import WAV:", self.filepath)
        #import_wav(self.filepath)
        print(self)
        print(context)
        args = {"filepath": self.filepath}
        result = bpy.ops.sound.open(**args)
        from pathlib import Path
        file_name = Path(self.filepath).name
        print(file_name)
        last = None
        for s in bpy.data.sounds:
            print(s)
            last = s
        sound = bpy.types.BlendDataSounds(last)
        import aud
        #sound = aud.Sound.file(file_name)
        print(sound)
        device = aud.Device()
        handle2 = device.play(sound)

        return {'FINISHED'}


ui_classes = [ PLAY_OT, FILE_SELECT_OT_rec, FILE_SELECT_OT_import_wav]

