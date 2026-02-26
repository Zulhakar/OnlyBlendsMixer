import bpy
from bl_ui import node_add_menu

from .cnt.node_editor.menus import GeometryMenu
from .cnt.node_editor import register as register_node_editor
from .cnt.node_editor import unregister as unregister_node_editor
from .cnt.sockets.basic_sockets import register as register_basic_sockets
from .cnt.sockets.basic_sockets import unregister as unregister_basic_sockets
from .cnt.nodes import register as register_nodes
from .cnt.nodes import unregister as unregister_nodes
from .cnt.node_editor.menus import InputMenu, GroupMenu, UtilMenu, RealtimeMenu

from .nodes import register as register_mixer_nodes
from .nodes import unregister as unregister_mixer_nodes

from .sockets import register as register_mixer_sockets
from .sockets import unregister as unregister_mixer_sockets

from .config import OB_TREE_TYPE, MixerSocketTypes, cnt_sockets_list, MIXER_MENU_IDNAME, MIDI_MENU_IDNAME

from .base.global_data import load_blend_file_job

cnt_sockets_list.append((MixerSocketTypes.Sample, "Sample", "Sample"))
cnt_sockets_list.append((MixerSocketTypes.Sound, "Sound", "Sound"))
cnt_sockets_list.append((MixerSocketTypes.Speaker, "Speaker", "Speaker"))

from bpy.utils import register_class
from bpy.utils import unregister_class


class MixerMenu(bpy.types.Menu):
    bl_label = "OnlyBlends.Mixer Nodes"
    bl_idname = MIXER_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "OscillatorSampleNode")
        node_add_menu.add_node_type(layout, "SampleToSoundNode")
        node_add_menu.add_node_type(layout, "SpeakerLinkNode")
        node_add_menu.add_node_type(layout, "SpeakerDataNode")
        node_add_menu.add_node_type(layout, "SampleToObjectNode")


class MixerGeometryMenu(GeometryMenu):
    bl_idname = f'NODE_MT_obm_GeometryMixer'

    def draw(self, context):
        super().draw(context)
        layout = self.layout



class MidiMenu(bpy.types.Menu):
    bl_label = "Midi"
    bl_idname = MIDI_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "NoteNode")


def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != OB_TREE_TYPE:
        return
    layout.menu(InputMenu.bl_idname)
    layout.menu(GroupMenu.bl_idname)
    layout.menu(UtilMenu.bl_idname)
    layout.menu(RealtimeMenu.bl_idname)
    # layout.menu(GeometryMenu.bl_idname)
    layout.menu(MixerGeometryMenu.bl_idname)
    layout.menu(MidiMenu.bl_idname)


def register():
    register_basic_sockets()
    register_nodes()
    register_mixer_sockets()
    register_mixer_nodes()
    register_node_editor()
    bpy.types.NODE_MT_add.append(draw_add_menu)
    register_class(MixerGeometryMenu)
    register_class(MidiMenu)
    bpy.app.handlers.load_post.append(load_blend_file_job)


def unregister():
    bpy.app.handlers.load_post.remove(load_blend_file_job)
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    unregister_class(MidiMenu)
    unregister_class(MixerGeometryMenu)
    unregister_basic_sockets()
    unregister_nodes()
    unregister_mixer_sockets()
    unregister_mixer_nodes()
    unregister_node_editor()


if __name__ == "__main__":
    register()
