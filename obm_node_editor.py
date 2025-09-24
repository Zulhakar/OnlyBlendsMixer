import bpy
from bpy.types import (Node, NodeCustomGroup, NodeTree, NodeSocket, Operator, NodeSocketGeometry,
                       NodeTreeInterfaceSocket, GeometryNodeTree, NodeGroupInput, NodeGroupOutput)
from bl_ui import node_add_menu

from .obm_nodes import (ImportWavNode, SoundInfoNode, SoundToSampleNode, EditSampleNode, OscillatorNode, \
                        CreateDeviceNode, \
                        PlayDeviceNode, CUSTOM_OT_actions, CUSTOM_UL_items, GatewayEntry, GatewayExit,
                        GeometryToSampleNode, SampleToSoundNode,
                        SampleInfoNode, SampleToGeometryNode, SampleToMeshNode, DeviceActionNode,
                        PLAY_DEVICE_OT_actions, PLAY_DEVICE_OT_actions2)

from .obm_sockets import WavImportSocket, NodeTreeInterfaceSocketWavImport, SoundSampleSocket, \
    NodeTreeInterfaceSocketSoundSample, DeviceSocket, NodeTreeInterfaceSocketDevice
from .basic_nodes import IntNode, FloatNode, StringNode, ObjectNode, BooleanNode
import aud


# Implementation of custom nodes from Python
def handle_muted_node(node):
    """
    Implements Blender-like bypass behavior for muted nodes.
    Each output will receive the value from the corresponding input if available,
    or fall back to input[0], or finally to 0.
    """
    # print(f"[Muted] Node '{node.name}' is bypassed.")

    for i, output_socket in enumerate(node.outputs):
        value = 0  # Fallback value

        # Prefer corresponding input socket
        if i < len(node.inputs) and node.inputs[i].is_linked:
            value = get_socket_value(node.inputs[i])

        # Fallback to input[0] if it's linked
        elif len(node.inputs) > 0 and node.inputs[0].is_linked:
            value = get_socket_value(node.inputs[0])

        output_socket.default_value = value


class ObmSoundTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'ObmSoundTreeType'
    bl_label = "OnlyBlends Sound Editor"
    bl_icon = 'SOUND'
    bl_use_group_interface = True
    color_tag = 'COLOR'


class ConstantsMenu(bpy.types.Menu):
    bl_label = 'Constants'
    bl_idname = 'obs.constants_node_menu'

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "ObmObjectNodeType")
        node_add_menu.add_node_type(layout, "ObmFloatNodeType")
        node_add_menu.add_node_type(layout, "ObmIntNodeType")
        node_add_menu.add_node_type(layout, "ObmStringNodeType")
        node_add_menu.add_node_type(layout, "ObmBooleanNodeType")


class DeviceMenu(bpy.types.Menu):
    bl_label = 'Device'
    bl_idname = 'obs.device_node_menu'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "PlayDeviceNodeType")
        node_add_menu.add_node_type(layout, "CreateDeviceNodeType")
        node_add_menu.add_node_type(layout, "DeviceActionNodeType")


class SampleMenu(bpy.types.Menu):
    bl_label = 'Sample'
    bl_idname = 'obs.sample_node_menu'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "SampleToGeometryType")
        node_add_menu.add_node_type(layout, "SampleToSoundNodeType")
        node_add_menu.add_node_type(layout, "CutSampleNodeType")
        node_add_menu.add_node_type(layout, "SampleToMeshType")
        node_add_menu.add_node_type(layout, "SampleInfoNodeType")

        layout.separator()
        node_add_menu.add_node_type(layout, "OscillatorNodeType")


class GatewayMenu(bpy.types.Menu):
    bl_label = 'Gateways'
    bl_idname = 'obs.gateways_node_menu'

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "GatewayEntryNodeType")
        node_add_menu.add_node_type(layout, "GatewayExitNodeType")


class SoundMenu(bpy.types.Menu):
    bl_label = 'Sounds'
    bl_idname = 'obs.sounds_node_menu'

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "SoundInfoNodeType")
        node_add_menu.add_node_type(layout, "SoundToSampleNodeType")


# Add custom nodes to the Add menu.
def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != ObmSoundTree.bl_idname:
        # Avoid adding nodes to built-in node tree
        return
    # Add nodes to the layout. Can use submenus, separators, etc. as in any other menu.

    # Device, Sample, Sound, ToObject/Geometry, Helper

    layout.menu(ConstantsMenu.bl_idname)
    layout.menu(DeviceMenu.bl_idname)
    layout.menu(SampleMenu.bl_idname)
    layout.menu(GatewayMenu.bl_idname)
    layout.menu(SoundMenu.bl_idname)

    node_add_menu.add_node_type(layout, "ImportWavNodeType")

    node_add_menu.add_node_type(layout, "GeometryToSampleType")


classes = [
    ObjectNode,
    FloatNode,
    IntNode,
    StringNode,
    BooleanNode,

    ObmSoundTree,
    SoundInfoNode,
    ImportWavNode, WavImportSocket, NodeTreeInterfaceSocketWavImport,
    SoundToSampleNode, SoundSampleSocket, NodeTreeInterfaceSocketSoundSample,
    EditSampleNode,
    OscillatorNode,
    PlayDeviceNode,

    DeviceActionNode, PLAY_DEVICE_OT_actions, PLAY_DEVICE_OT_actions2,

    CreateDeviceNode, DeviceSocket, NodeTreeInterfaceSocketDevice,

    GatewayEntry, GatewayExit,
    CUSTOM_UL_items, CUSTOM_OT_actions,

    GeometryToSampleNode,

    SampleToSoundNode,

    SampleInfoNode,
    SampleToGeometryNode,

    SampleToMeshNode,

    ConstantsMenu,
    DeviceMenu,
    SampleMenu,
    GatewayMenu,
    SoundMenu
]


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.NODE_MT_add.append(draw_add_menu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
