import bpy
from bpy.utils import register_class, unregister_class

from .sample_socket import (NodeSocketSample, NodeTreeInterfaceSocketSample,
                            NodeSocketSoundObm, NodeTreeInterfaceSocketSoundObm, NodeSocketSpeaker,
                            NodeTreeInterfaceSocketSpeaker)
from .import_midi_socket import NodeSocketImportMidi, NodeTreeInterfaceSocketImportMidi
from .midi_socket import NodeSocketMidi, NodeTreeInterfaceSocketMidi

sockets = [NodeSocketSample, NodeTreeInterfaceSocketSample, NodeSocketSoundObm, NodeTreeInterfaceSocketSoundObm,
           NodeSocketSpeaker, NodeTreeInterfaceSocketSpeaker,
           NodeSocketImportMidi, NodeTreeInterfaceSocketImportMidi, NodeSocketMidi, NodeTreeInterfaceSocketMidi]


def register():
    for socket in sockets:
        bpy.utils.register_class(socket)


def unregister():
    for socket in sockets:
        bpy.utils.unregister_class(socket)
