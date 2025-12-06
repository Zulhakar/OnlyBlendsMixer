import bpy
from .obm_nodes import (ImportWavNode, SoundInfoNode, SoundToSampleNode, CreateDeviceNode, \
                        PlayDeviceNode,
                        SampleInfoNode, SampleToGeometryNode, SampleToMeshNode, DeviceActionNode,
                        PLAY_DEVICE_OT_actions, PLAY_DEVICE_OT_actions2)

from .nodes.constant_nodes.speaker_node import SpeakerNode

from .nodes.sample_nodes.sample_to_sound_node import SampleToSoundNode
from .nodes.sample_nodes.oscillator_node import OscillatorNode
from .nodes.sample_nodes.edit_node import EditSampleNode
from .nodes.sample_nodes.sample_sequencer import NoteSequenceToSampleNode, NodeSocketCollectionItem
from .nodes.sample_nodes.geometry_to_sample_node import (GeometryToSampleNode, GeometryGroupInputCollectionItem,
                                                         CUSTOM_UL_geometry_group_input_items)
from .nodes.group_nodes.group_node import GroupNodeObm

from .nodes.speaker_nodes.speaker_link_node import SpeakerLinkNode
from .nodes.basic_nodes import IntNode, FloatNode, StringNode, ObjectNode, BooleanNode
from .nodes.constant_nodes.note_to_frequency_node import NoteToFrequencyNode
from .nodes.constant_nodes.vector_node import VectorNode
from .nodes.constant_nodes.combine_xyz_node import CombineXyzNode
from .nodes.constant_nodes.note_sequence_node import KeySequenceNode
import aud
from bpy.utils import register_class

classes = [
    ObjectNode,
    FloatNode,
    IntNode,
    StringNode,
    BooleanNode,
    VectorNode,
    NoteToFrequencyNode,
    SpeakerNode,
    SpeakerLinkNode,
    GroupNodeObm,
    KeySequenceNode,
    CombineXyzNode,
    #SoundInfoNode,
    #ImportWavNode, WavImportSocket, NodeTreeInterfaceSocketWavImport,

    SoundToSampleNode,
    EditSampleNode,
    OscillatorNode,
    NodeSocketCollectionItem,  NoteSequenceToSampleNode,

    PlayDeviceNode,

    #DeviceActionNode, PLAY_DEVICE_OT_actions, PLAY_DEVICE_OT_actions2,

    #CreateDeviceNode, DeviceSocket, NodeTreeInterfaceSocketDevice,


    GeometryGroupInputCollectionItem, CUSTOM_UL_geometry_group_input_items, GeometryToSampleNode,

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
