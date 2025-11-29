import bpy

from .nodes.constant_nodes.speaker_node import SpeakerNode
from .obm_nodes import (ImportWavNode, SoundInfoNode, SoundToSampleNode, CreateDeviceNode, \
                        PlayDeviceNode, CUSTOM_OT_actions, CUSTOM_UL_items, GatewayEntry, GatewayExit,
                        GeometryToSampleNode, SampleInfoNode, SampleToGeometryNode, SampleToMeshNode, DeviceActionNode,
                        PLAY_DEVICE_OT_actions, PLAY_DEVICE_OT_actions2)
from .nodes.sample_nodes.sample_to_sound_node import SampleToSoundNode
from .nodes.sample_nodes.oscillator_node import OscillatorNode
from .nodes.sample_nodes.edit_node import EditSampleNode
from .nodes.sample_nodes.sample_sequencer import NoteSequenceToSampleNode
from .nodes.group_nodes.group_node import GroupNodeObm

from .nodes.speaker_nodes.speaker_link_node import SpeakerLinkNode
from .obm_sockets import WavImportSocket, NodeTreeInterfaceSocketWavImport, SoundSampleSocket, \
    NodeTreeInterfaceSocketSoundSample, DeviceSocket, NodeTreeInterfaceSocketDevice
from .nodes.basic_nodes import IntNode, FloatNode, StringNode, ObjectNode, BooleanNode
from .nodes.constant_nodes.note_node import NoteNode
import aud
from bpy.utils import register_class

classes = [
    ObjectNode,
    FloatNode,
    IntNode,
    StringNode,
    BooleanNode,
    NoteNode,
    SpeakerNode,
    SpeakerLinkNode,
    GroupNodeObm,


    #SoundInfoNode,
    #ImportWavNode, WavImportSocket, NodeTreeInterfaceSocketWavImport,

    SoundToSampleNode, SoundSampleSocket, NodeTreeInterfaceSocketSoundSample,
    EditSampleNode,
    OscillatorNode,
    NoteSequenceToSampleNode,

    PlayDeviceNode,

    #DeviceActionNode, PLAY_DEVICE_OT_actions, PLAY_DEVICE_OT_actions2,

    #CreateDeviceNode, DeviceSocket, NodeTreeInterfaceSocketDevice,

    #GatewayEntry, GatewayExit,
    #CUSTOM_UL_items, CUSTOM_OT_actions,

    GeometryToSampleNode,

    SampleToSoundNode,

    #SampleInfoNode,
    #SampleToGeometryNode,

    SampleToMeshNode,

]


def register():
    from bpy.utils import register_class
    from .node_editor import register
    for cls in classes:
        print(cls.__name__)
        register_class(cls)
    register()


def unregister():
    from bpy.utils import unregister_class
    from .node_editor import unregister
    for cls in reversed(classes):
        unregister_class(cls)
    unregister()
