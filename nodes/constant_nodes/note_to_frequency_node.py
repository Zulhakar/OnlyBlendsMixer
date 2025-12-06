import bpy

from ...helper import create_note_dict, create_note_enum_items
from ..basic_nodes import ObmConstantNode


class NoteToFrequencyNode(ObmConstantNode):
    '''Note Node'''
    bl_label = "Note To Frequency"

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
        frequency_socket = self.outputs.new('FloatSocketType', "Float")
        frequency_socket.is_constant = True

        self.note_update()
        super().init(context)