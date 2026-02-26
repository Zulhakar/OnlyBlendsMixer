import bpy
import aud
import copy
from ..config import APP_NAME_SHORT, NOTE_NAMES_1, NOTE_NAMES_2


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

def create_note_dict():
    # source: https://en.wikipedia.org/wiki/Piano_key_frequencies
    octaves_num = 9
    notes_num = 12
    names_1 = NOTE_NAMES_1
    names_2 = NOTE_NAMES_2
    current_index = 0
    midi_note_index = 12
    piano_key_number_index = -8

    notes_table = {}
    for octave in range(octaves_num):
        for note_index in range(notes_num):
            current_note_name1 = names_1[note_index] + str(octave)
            current_note_name2 = names_2[note_index] + str(octave)
            frequency = ((2 ** (1 / 12)) ** (piano_key_number_index - 49)) * 440
            notes_table[current_note_name1] = (current_note_name1, current_note_name2, midi_note_index,
                                               piano_key_number_index, frequency)
            current_index += 1
            midi_note_index += 1
            piano_key_number_index += 1

    return notes_table, ("name1", "name2", "midi_note_index", "piano_key_number_index", "frequency")


def create_note_enum_items(notes_table):
    notes = []
    for key, value in notes_table.items():
        description = f"Note: {value[0]}/{value[1]}, Frequency: {value[4]} Hz, Midi Note Index: {value[2]}, Piano Key: {value[3]}"
        notes.append((value[0], value[0],
                      description))
    # sorted_notes = sorted(notes, key=lambda item: item[2])
    return notes