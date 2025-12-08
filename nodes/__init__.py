from .obm_nodes import SoundToSampleNode, PlayDeviceNode, SampleToMeshNode

from .constant_nodes.speaker_node import SpeakerNode

from .sample_nodes.sample_to_sound_node import SampleToSoundNode
from .sample_nodes.oscillator_node import OscillatorSampleNode
from .sample_nodes.edit_node import EditSampleNode
from .sample_nodes.sample_sequencer import NoteSequenceToSampleNode, NodeSocketCollectionItem
from .sample_nodes.geometry_to_sample_node import (GeometryToSampleNode, GeometryGroupInputCollectionItem,
                                                         CUSTOM_UL_geometry_group_input_items)
from .group_nodes.group_node import GroupNodeObm

from .speaker_nodes.speaker_link_node import SpeakerLinkNode
from .basic_nodes import IntNode, FloatNode, StringNode, ObjectNode, BooleanNode
from .constant_nodes.note_to_frequency_node import NoteToFrequencyNode
from .constant_nodes.vector_node import VectorNode
from .constant_nodes.combine_xyz_node import CombineXyzNode
from .constant_nodes.note_sequence_node import KeySequenceNode

from .constant_nodes.math_node import MathNode
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
    MathNode,
    #SoundInfoNode,
    #ImportWavNode, WavImportSocket, NodeTreeInterfaceSocketWavImport,

    SoundToSampleNode,
    EditSampleNode,
    OscillatorSampleNode,
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

