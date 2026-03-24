import bpy
from bl_ui import node_add_menu
from bpy.utils import register_class
from bpy.utils import unregister_class

from .cnt.node_editor import register as register_node_editor
from .cnt.node_editor import unregister as unregister_node_editor
from .cnt.sockets import register as register_basic_sockets
from .cnt.sockets import unregister as unregister_basic_sockets
from .cnt.nodes import register as register_nodes
from .cnt.nodes import unregister as unregister_nodes
from .cnt.node_editor.menus import InputMenu, GroupMenu, UtilMenu, RealtimeMenu

from .nodes import register as register_mixer_nodes
from .nodes import unregister as unregister_mixer_nodes

from .sockets import register as register_mixer_sockets
from .sockets import unregister as unregister_mixer_sockets

from .config import OB_TREE_TYPE, MixerSocketTypes, cnt_sockets_list, MIXER_MENU_IDNAME, MIDI_MENU_IDNAME

cnt_sockets_list.append((MixerSocketTypes.Sample, "Sample", "Sample"))
cnt_sockets_list.append((MixerSocketTypes.Sound, "Sound", "Sound"))
cnt_sockets_list.append((MixerSocketTypes.Speaker, "Speaker", "Speaker"))


class SampleMenu(bpy.types.Menu):
    bl_label = "Sample"
    bl_idname = f'NODE_MT_obm_Sample'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "OscillatorSampleNode")
        node_add_menu.add_node_type(layout, "EditSampleNode")
        node_add_menu.add_node_type(layout, "TrackSampleNode")
        node_add_menu.add_node_type(layout, "ObjectToSampleNode")
        node_add_menu.add_node_type(layout, "SampleToObjectNode")
        node_add_menu.add_node_type(layout, "SoundToSampleNode")


class SoundMenu(bpy.types.Menu):
    bl_label = "Sound"
    bl_idname = f'NODE_MT_obm_Sound'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "SampleToSoundNode")
        node_add_menu.add_node_type(layout, "ImportSoundNodeObm")


class ObMixerMenu(bpy.types.Menu):
    bl_label = "Mixer"
    bl_idname = f'NODE_MT_obm_Mixer'

    def draw(self, context):
        layout = self.layout
        layout.menu(SampleMenu.bl_idname)
        layout.menu(SoundMenu.bl_idname)
        layout.menu(SpeakerMenu.bl_idname)
        layout.menu(MidiMenu.bl_idname)


class SpeakerMenu(bpy.types.Menu):
    bl_label = "Speaker"
    bl_idname = f'NODE_MT_obm_Speaker'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "SpeakerLinkNode")
        node_add_menu.add_node_type(layout, "SpeakerDataNode")


class MidiMenu(bpy.types.Menu):
    bl_label = "Midi"
    bl_idname = MIDI_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "NoteNode")
        node_add_menu.add_node_type(layout, "ImportMidiNode")
        node_add_menu.add_node_type(layout, "MidiToTrackObjectNode")


def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != OB_TREE_TYPE:
        return
    layout.menu(InputMenu.bl_idname)
    layout.menu(GroupMenu.bl_idname)
    layout.menu(UtilMenu.bl_idname)
    layout.menu(RealtimeMenu.bl_idname)
    node_add_menu.add_node_type(layout, "ModifierNode")
    layout.menu(ObMixerMenu.bl_idname)


def register():
    register_basic_sockets()
    register_nodes()
    register_mixer_sockets()
    register_mixer_nodes()
    register_node_editor()
    bpy.types.NODE_MT_add.append(draw_add_menu)
    register_class(SampleMenu)
    register_class(SpeakerMenu)
    register_class(MidiMenu)
    register_class(SoundMenu)
    register_class(ObMixerMenu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    unregister_class(ObMixerMenu)
    unregister_class(SoundMenu)
    unregister_class(MidiMenu)
    unregister_class(SampleMenu)
    unregister_class(SpeakerMenu)
    unregister_basic_sockets()
    unregister_nodes()
    unregister_mixer_sockets()
    unregister_mixer_nodes()
    unregister_node_editor()


if __name__ == "__main__":
    register()
