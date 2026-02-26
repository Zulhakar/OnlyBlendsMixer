import bpy
import aud
import copy
from ..config import APP_NAME_SHORT


def get_parent_node_group(in_node):
    for key, value in bpy.data.node_groups.items():
        for node in value.nodes:
            if node == in_node:
                return value
    return None


def get_node_id_name(node):
    parent = get_parent_node_group(node)
    node_name = f"{APP_NAME_SHORT}_{parent.name}_{node.name}"
    return node_name


def get_length_and_specs_from_sound(sound):
    sound_aud = aud.Sound(sound.filepath)
    length = copy.deepcopy(sound_aud.length)
    specs = copy.deepcopy(sound_aud.specs)
    del sound_aud
    return length, specs
