import bpy
from bl_ui import node_add_menu
from ..core.constants import SOUND_TREE_TYPE

class ConstantsMenu(bpy.types.Menu):
    bl_label = 'Constants'
    bl_idname = 'NODE_MT_Obm_Constants'

    def draw(self, context):
        layout = self.layout

        #node_add_menu.add_node_type(layout, "ObmObjectNodeType")
        node_add_menu.add_node_type(layout, "ObmFloatNodeType")
        node_add_menu.add_node_type(layout, "ObmIntNodeType")
        node_add_menu.add_node_type(layout, "ObmStringNodeType")
        node_add_menu.add_node_type(layout, "ObmBooleanNodeType")
        layout.separator()
        node_add_menu.add_node_type(layout, "ObmVectorNodeType")
        node_add_menu.add_node_type(layout, "ObmCombineXyzNodeType")
        layout.separator()
        node_add_menu.add_node_type(layout, "NoteToFrequencyNode")

        # example to set default size of Value Node
        # props = node_add_menu.add_node_type(layout, "ObmFloatNodeType")
        # ops = props.settings.add()
        # ops.name = "width"
        # ops.value = "350"


class DeviceMenu(bpy.types.Menu):
    bl_label = 'Device'
    bl_idname = 'NODE_MT_Obm_Devices'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "PlayDeviceNodeType")
        node_add_menu.add_node_type(layout, "CreateDeviceNodeType")
        node_add_menu.add_node_type(layout, "DeviceActionNodeType")


class SampleMenu(bpy.types.Menu):
    bl_label = 'Sample'
    bl_idname = 'NODE_MT_Obm_Samples'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "OscillatorSampleNode")
        layout.separator()
        node_add_menu.add_node_type(layout, "EditSampleNode")
        node_add_menu.add_node_type(layout, "SampleToSoundNode")
        layout.separator()
        node_add_menu.add_node_type(layout, "NoteSequenceToSampleNodeType")
        # node_add_menu.add_node_type(layout, "SampleInfoNodeType")
        layout.separator()
        #node_add_menu.add_node_type(layout, "SampleToGeometryType")
        node_add_menu.add_node_type(layout, "SampleToMeshType")
        node_add_menu.add_node_type(layout, "GeometryToSampleType")


class SpeakerMenu(bpy.types.Menu):
    bl_label = 'Speaker'
    bl_idname = 'NODE_MT_Obm_Speakers'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "SpeakerLinkNode")
        node_add_menu.add_node_type(layout, "SpeakerDataNode")
        node_add_menu.add_node_type(layout, "SpeakerNodeType")


class SoundMenu(bpy.types.Menu):
    bl_label = 'Sounds'
    bl_idname = 'NODE_MT_Obm_Sounds'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "SoundInfoNodeType")
        node_add_menu.add_node_type(layout, "SoundToSampleNodeType")

class InputMenu(bpy.types.Menu):
    bl_label = 'Input'
    bl_idname = 'NODE_MT_Obm_Input'
    def draw(self, context):
        layout = self.layout
        layout.menu(ConstantsMenu.bl_idname)
        node_add_menu.add_node_type(layout, "NodeGroupInput")
        node_add_menu.add_node_type(layout, "GeometryToSampleType")

class OutputMenu(bpy.types.Menu):
    bl_label = 'Output'
    bl_idname = 'NODE_MT_Obm_Output'
    def draw(self, context):
        layout = self.layout
        layout.menu(ConstantsMenu.bl_idname)
        node_add_menu.add_node_type(layout, "NodeGroupOutput")

class GroupMenu(bpy.types.Menu):
    bl_label = 'Group'
    bl_idname = 'NODE_MT_Obm_Group'
    def draw(self, context):
        layout = self.layout
        #layout.menu(ConstantsMenu.bl_idname)
        node_add_menu.add_node_type(layout, "NodeGroupInput")
        node_add_menu.add_node_type(layout, "NodeGroupOutput")
        node_add_menu.add_node_type(layout, "GroupNodeObm")
        #self.layout.operator("node.my_make_group",text='Group', icon='ADD')

class NoteMenu(bpy.types.Menu):
    bl_label = 'Note'
    bl_idname = 'NODE_MT_Obm_Note'
    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "NoteToFrequencyNode")
        node_add_menu.add_node_type(layout, "NoteSequenceNode")
        node_add_menu.add_node_type(layout, "NoteSequenceToSampleNodeType")

def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != SOUND_TREE_TYPE:
        # Avoid adding nodes to built-in node tree
        return
    # Add nodes to the layout. Can use submenus, separators, etc. as in any other menu.

    # Device, Sample, Sound, ToObject/Geometry, Helper

    layout.menu(InputMenu.bl_idname)
    layout.menu(NoteMenu.bl_idname)
    layout.menu(SpeakerMenu.bl_idname)
    # layout.menu(DeviceMenu.bl_idname)
    layout.menu(SampleMenu.bl_idname)
    layout.menu(GroupMenu.bl_idname)
    node_add_menu.add_node_type(layout, "MathNode")
    # layout.menu(SoundMenu.bl_idname)

    #node_add_menu.add_node_type(layout, "ImportWavNodeType")
    #layout.separator()



def menu_draw(self, context):
    tree = context.space_data.node_tree
    if tree and tree.bl_idname == SOUND_TREE_TYPE:
        self.layout.operator("node.my_make_group",
                             text="Make Group",
                             icon='NODETREE')
