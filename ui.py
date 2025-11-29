import bpy
import mathutils
from bpy_extras.io_utils import ImportHelper

from .helper import play_selection, import_wav
# wild and evil
from .constants import *


class MainPt(OnlyBlendsPanel, bpy.types.Panel):
    bl_label = APP_NAME
    bl_idname = MAIN_PT_ID

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mixer_props = scene.mixer_props
        # Checkboxes
        if mixer_props.enable_mixer_loop:
            layout.prop(mixer_props, 'enable_mixer_loop', icon=STOP_ICON, toggle=True)
        else:
            layout.prop(mixer_props, 'enable_mixer_loop', icon=RECORD_ICON, toggle=True)
        layout.prop(mixer_props, 'start_play_animation')
        # layout.prop(mixer_props, "play_duration")

        r = layout.row()
        r.prop(mixer_props, 'record_file_path', text="")
        r.operator(FILE_REC_OT_ID, icon=FILE_ICON, text="")
        if mixer_props.enable_mixer_loop:
            layout.label(text="Recording ...", icon=RECORD_ICON)
            # layout.label(text=f"Iterations: {mixer_props.iteration_count}")
            layout.label(text=f"Duration: {mixer_props.record_duration}")
            layout.label(text=f"Sample Duration: {mixer_props.play_duration}")
        else:
            layout.label(text="Pause", icon=STOP_ICON)
        op_model = layout.operator(PLAY_OT_ID, text="Play Selected Object", icon=PLAY_ICON)


class SUB1_PT(OnlyBlendsPanel, bpy.types.Panel):
    bl_label = SUB1_PT_label
    bl_idname = SUB1_PT_ID
    bl_parent_id = MAIN_PT_ID

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mixer_props = scene.mixer_props
        layout.label(text="Import:")
        box = layout.box()
        r = box.row()
        #r.prop(mixer_props, 'import_wav_file_path', text="")
        r.operator(FILE_IMPORT_OT_ID, icon=FILE_ICON, text="")


class SUB2_PT(OnlyBlendsPanel, bpy.types.Panel):
    bl_label = SUB2_PT_label
    bl_idname = SUB2_PT_ID
    bl_parent_id = MAIN_PT_ID

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mixer_props = scene.mixer_props
        layout.label(text="Setting:")

        # box = layout.box()
        # r = box.row()
        # r.prop(mixer_props, "import_wav_file_path", text="")
        # r.operator("ob.file_select_ot_import_wav", icon="FILE", text="")


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


class CUSTOM_OT_clearList(bpy.types.Operator):
    """Clear all items of the list"""
    bl_idname = "custom.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items of the list"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.custom):
            context.scene.custom.clear()
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return {'FINISHED'}


class CUSTOM_UL_items2(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.5)

        split.label(text="sadfdf")
        custom_icon = "OUTLINER_OB_%s" % item.obj_type
        # split.prop(item, "name", text="", emboss=False, translate=False, icon=custom_icon)
        split.label(text=item.name,)  # avoids renaming the item by accident

    def invoke(self, context, event):
        pass


class CUSTOM_PT_objectList(OnlyBlendsPanel, bpy.types.Panel):
    """Adds a custom panel to the TEXT_EDITOR"""
    bl_idname = 'TEXT_PT_my_panel'
    bl_label = "Custom Object List Demo"
    bl_parent_id = MAIN_PT_ID

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("CUSTOM_UL_items", "", scn, "custom", scn, "custom_index", rows=rows)

        col = row.column(align=True)
        col.operator("custom.list_action", icon='ZOOM_IN', text="").action = 'ADD'
        col.operator("custom.list_action", icon='ZOOM_OUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)
        # row.operator("custom.print_items", icon="LINENUMBERS_ON") #LINENUMBERS_OFF, ANIM
        # row = col.row(align=True)
        # row.operator("custom.select_items", icon="VIEW3D", text="Select Item")
        # row.operator("custom.select_items", icon="GROUP", text="Select all Items").select_all = True
        # row = col.row(align=True)
        row.operator("custom.clear_list", icon="X")
        # row.operator("custom.remove_duplicates", icon="GHOST_ENABLED")


# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------
class CUSTOM_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.custom) - 1:
                item_next = scn.custom[idx + 1].name
                scn.custom.move(idx, idx + 1)
                scn.custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx - 1].name
                scn.custom.move(idx, idx - 1)
                scn.custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scn.custom[idx].name)
                scn.custom_index -= 1
                scn.custom.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            if context.object:
                item = scn.custom.add()
                item.name = context.object.name
                item.obj_type = context.object.type
                item.obj_id = len(scn.custom)
                scn.custom_index = len(scn.custom) - 1
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
            else:
                self.report({'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}

# PLAY_OT,
ui_classes = [MainPt, SUB1_PT, SUB2_PT, PLAY_OT, FILE_SELECT_OT_rec, FILE_SELECT_OT_import_wav,
              CUSTOM_UL_items2, CUSTOM_PT_objectList, CUSTOM_OT_clearList, CUSTOM_OT_actions]

