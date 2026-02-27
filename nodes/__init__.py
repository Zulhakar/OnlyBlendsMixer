import bpy
from bpy.utils import register_class
from bpy.utils import unregister_class

from .sample_nodes.edit_node import EditSampleNode
from .sample_nodes.oscillator_node import OscillatorSampleNode
from .sample_nodes.sample_to_sound_node import SampleToSoundNode
from .speaker_nodes.speaker_link_node import SpeakerLinkNode
from .speaker_nodes.speaker_data_node import SpeakerDataNode
from .geometry.sample_to_object import SampleToObjectNode
from .geometry.gn_track_node import ObjectTrackNode
from .midi_nodes.note_node import NoteNode
nodes = [OscillatorSampleNode, SampleToSoundNode, SpeakerLinkNode, SpeakerDataNode, SampleToObjectNode, EditSampleNode,
         NoteNode, ObjectTrackNode]


def register():
    for node in nodes:
        bpy.utils.register_class(node)


def unregister():
    for node in nodes:
        bpy.utils.unregister_class(node)
