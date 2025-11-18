import bpy
from bpy.types import NodeCustomGroup
from ..constants import IS_DEBUG


class ObmSoundNode:

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ObmSoundTreeType'

    def copy(self, node):
        if IS_DEBUG:
            print(f"Copying from node {self.bl_idname}")

    def free(self):
        if IS_DEBUG:
            print(f"Removing node {self.bl_idname}")

    def refresh_outputs(self):
        if IS_DEBUG:
            print(f"refresh outputs {self.bl_idname}")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        if IS_DEBUG:
            print(f"link {self.bl_idname}")

    def update(self):
        if IS_DEBUG:
            print(f"update {self.bl_idname}")

    def socket_update(self, socket):
        if IS_DEBUG:
            print(f"socket_update {self.bl_idname}")

    def update_obm(self):
        if IS_DEBUG:
            print(f"update_obm {self.bl_idname}")


class ObmConstantNode(ObmSoundNode, NodeCustomGroup):
    def socket_update(self, socket):
        super().socket_update(socket)
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value
            link.to_node.update_obm()


class ObjectNode(ObmConstantNode):
    '''Object Node'''
    bl_idname = 'ObmObjectNodeType'
    bl_label = "Object"

    def init(self, context):
        self.outputs.new('ObjectSocketConstantType', "Object")


class FloatNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmFloatNodeType'
    bl_label = "Value"

    def init(self, context):
        self.outputs.new('FloatSocketConstantType', "Float")


def create_note_dict():
    # source: https://en.wikipedia.org/wiki/Piano_key_frequencies
    octaves_num = 9
    notes_num = 12
    names_1 = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    names_2 = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
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


class NoteNode(ObmConstantNode):
    '''Note Node'''
    bl_idname = 'ObmNoteNodeType'
    bl_label = "Note Frequency"

    notes_dict = create_note_dict()[0]

    note: bpy.props.EnumProperty(  # type: ignore
        name="Note"
        , items=create_note_enum_items(notes_dict)
        , default="A2"
        , update=lambda self, context: self.note_update())

    def note_update(self):
        self.outputs[0].input_value = self.notes_dict[self.note][4]

    def draw_buttons(self, context, layout):
        layout.prop(self, "note", text="Note")

    def init(self, context):
        self.outputs.new('FloatSocketConstantType', "Float")
        self.note_update()


class IntNode(ObmConstantNode):
    '''Value Node'''
    bl_idname = 'ObmIntNodeType'
    bl_label = "Integer"

    def init(self, context):
        self.outputs.new('IntSocketConstantType', "Integer")


class StringNode(ObmConstantNode):
    '''Float Value Node'''
    bl_idname = 'ObmStringNodeType'
    bl_label = "String"

    def init(self, context):
        self.outputs.new('StringSocketConstantType', "String")


class BooleanNode(ObmConstantNode):
    '''Boolean Value Node'''
    bl_idname = 'ObmBooleanNodeType'
    bl_label = "Boolean"

    def init(self, context):
        self.outputs.new('BoolSocketConstantType', "Boolean")
