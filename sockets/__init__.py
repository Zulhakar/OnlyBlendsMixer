import bpy
from bpy.utils import register_class, unregister_class

from .sample_socket import (NodeSocketSample, NodeTreeInterfaceSocketSample,
                            NodeSocketSound, NodeTreeInterfaceSocketSound, NodeSocketSpeaker,
                            NodeTreeInterfaceSocketSpeaker)

sockets = [NodeSocketSample, NodeTreeInterfaceSocketSample, NodeSocketSound, NodeTreeInterfaceSocketSound,
           NodeSocketSpeaker, NodeTreeInterfaceSocketSpeaker]


def register():
    for socket in sockets:
        bpy.utils.register_class(socket)


def unregister():
    for socket in sockets:
        bpy.utils.unregister_class(socket)
