import bpy
from bpy.types import (Node, NodeCustomGroup, NodeTree, NodeSocket, Operator, NodeSocketGeometry,
                       NodeTreeInterfaceSocket, GeometryNodeTree, NodeGroupInput, NodeGroupOutput)
from bl_ui import node_add_menu

from .obm_nodes import (ImportWavNode, SoundInfoNode, SoundToSampleNode, EditSampleNode, OscillatorNode, \
                        CreateDeviceNode, \
                        PlayDeviceNode, CUSTOM_OT_actions, CUSTOM_UL_items, GatewayEntry, GatewayExit,
                        SoundFromGeometry, SampleToSoundNode,
                        SampleInfoNode, SoundToGeometry, SoundSampleToMeshNode)
from .obm_sockets import WavImportSocket, NodeTreeInterfaceSocketWavImport, SoundSampleSocket, \
    NodeTreeInterfaceSocketSoundSample, DeviceSocket, NodeTreeInterfaceSocketDevice
from .basic_nodes import IntNode, FloatNode, StringNode, ObjectNode
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
    #   print(f" → Output[{i}] = {value}")


# def get_socket_value(socket: NodeSocket):
#     """
#     Retrieves the value from a socket, recursively following links (e.g., through Reroute nodes).
#     It fetches the *actual* data value from the source of the link or the socket's default value.
#     Converts the value to the expected type based on the target socket's type.
#     """
#     current_socket = socket
#
#     # Traverse through linked sockets until we find the actual data source
#     # or an unlinked socket
#     while current_socket.is_linked:
#         from_socket = current_socket.links[0].from_socket
#
#         # If the 'from_socket' is an output of a Reroute node,
#         # we need to go to its input to find the true source.
#         # Otherwise, the from_socket itself is our next candidate.
#         if hasattr(from_socket.node, 'bl_idname') and from_socket.node.bl_idname == 'NodeReroute':
#             # A Reroute node's output socket doesn't hold a value directly.
#             # Its value comes from its *single input socket*.
#             # So, we set the current_socket to the Reroute's input socket
#             # to continue tracing the connection backward.
#             if from_socket.node.inputs[0].is_linked:
#                 current_socket = from_socket.node.inputs[0].links[0].from_socket
#             else:
#                 # Reroute node's input is not linked, so it provides no value
#                 current_socket = None  # Break the loop, effectively meaning no value
#                 break
#         else:
#             # If it's not a Reroute node, then this 'from_socket' is our actual source.
#             current_socket = from_socket
#             break  # Found the source, exit the loop
#
#     val = None
#     if current_socket:
#         # Now current_socket should be the source socket
#         if hasattr(current_socket, "default_value"):
#             val = current_socket.default_value
#
#     # --- Type Conversion based on Target Socket Type ---
#
#     if val is not None:
#         if isinstance(socket, (NodeSocketFloat)):
#             if isinstance(val, (tuple, list, bpy.types.bpy_prop_array)) and hasattr(val, '__len__') and len(val) > 0:
#                 # Take the first component if it's an array/tuple (e.g., from a vector or color output)
#                 return float(val[0])  # type: ignore
#
#             return float(val) if val is not None else 0.0
#
#         elif isinstance(socket, (NodeSocketInt)):
#             if isinstance(val, (tuple, list, bpy.types.bpy_prop_array)) and hasattr(val, '__len__') and len(val) > 0:
#                 return int(val[0])  # type: ignore
#
#             return int(val) if val is not None else 0
#
#         elif isinstance(socket, (NodeSocketColor)):
#             if isinstance(val, (tuple, list, bpy.types.bpy_prop_array)):
#                 if len(val) == 3:
#                     return (*val, 1.0)  # Add default alpha
#                 elif len(val) == 4:
#                     return tuple(val)
#                 return val if val is not None else (0.7, 0.7, 0.7, 1)
#
#         # elif isinstance(socket, NodeSocketInt) or isinstance(socket, CCNCustomIntegerSocket):
#         #     return int(val) if val is not None else 0
#
#     return val  # Return for other socket types


class ObmSoundTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'ObmSoundTreeType'
    bl_label = "OnlyBlends Sound Editor"
    bl_icon = 'SOUND'
    bl_use_group_interface = True
    color_tag = 'COLOR'


# Add custom nodes to the Add menu.
def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != ObmSoundTree.bl_idname:
        # Avoid adding nodes to built-in node tree
        return
    # Add nodes to the layout. Can use submenus, separators, etc. as in any other menu.

    node_add_menu.add_node_type(layout, "ObmObjectNodeType")
    node_add_menu.add_node_type(layout, "ObmFloatNodeType")
    node_add_menu.add_node_type(layout, "ObmIntNodeType")
    node_add_menu.add_node_type(layout, "ObmStringNodeType")

    node_add_menu.add_node_type(layout, "SoundInfoNodeType")
    node_add_menu.add_node_type(layout, "ImportWavNodeType")

    node_add_menu.add_node_type(layout, "SoundToSampleNodeType")
    node_add_menu.add_node_type(layout, "SampleToSoundNodeType")

    node_add_menu.add_node_type(layout, "CutSampleNodeType")

    node_add_menu.add_node_type(layout, "OscillatorNodeType")
    node_add_menu.add_node_type(layout, "PlayDeviceNodeType")
    node_add_menu.add_node_type(layout, "CreateDeviceNodeType")

    node_add_menu.add_node_type(layout, "GatewayEntryNodeType")
    node_add_menu.add_node_type(layout, "GatewayExitNodeType")

    node_add_menu.add_node_type(layout, "SoundFromGeometryType")

    node_add_menu.add_node_type(layout, "SampleInfoNodeType")
    node_add_menu.add_node_type(layout, "SoundToGeometryType")
    # SoundSampleToMeshType
    node_add_menu.add_node_type(layout, "SoundSampleToMeshType")

    # node_add_menu.draw_node_group_add_menu(context, layout)


classes = [
    ObjectNode,
    FloatNode,
    IntNode,
    StringNode,

    ObmSoundTree,
    SoundInfoNode,
    ImportWavNode, WavImportSocket, NodeTreeInterfaceSocketWavImport,
    SoundToSampleNode, SoundSampleSocket, NodeTreeInterfaceSocketSoundSample,
    EditSampleNode,
    OscillatorNode,
    PlayDeviceNode,
    CreateDeviceNode, DeviceSocket, NodeTreeInterfaceSocketDevice,

    GatewayEntry, GatewayExit,
    CUSTOM_UL_items, CUSTOM_OT_actions,

    SoundFromGeometry,

    SampleToSoundNode,

    SampleInfoNode,
    SoundToGeometry,

    SoundSampleToMeshNode
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
