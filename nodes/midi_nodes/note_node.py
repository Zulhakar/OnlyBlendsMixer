import bpy

from ...base.helper import create_note_dict, create_note_enum_items
from ..mixer_node import ObmSoundNode


class NoteNode(ObmSoundNode, bpy.types.Node):
    '''Note Node'''
    bl_label = "Note"

    notes_dict = create_note_dict()[0]

    note: bpy.props.EnumProperty(  # type: ignore
        name="Note"
        , items=create_note_enum_items(notes_dict)
        , default="A2"
        , update=lambda self, context: self.note_update())

    def note_update(self):
        self.outputs[0].input_value = self.notes_dict[self.note][4]
        self.outputs[1].input_value = self.notes_dict[self.note][2]
        self.outputs[2].input_value = self.notes_dict[self.note][0]
        self.outputs[3].input_value = self.notes_dict[self.note][1]

    def draw_buttons(self, context, layout):
        layout.prop(self, "note", text="Note")

    def init(self, context):
        self.outputs.new('NodeSocketFloatCnt', "Frequency")
        self.outputs.new("NodeSocketIntCnt", "Midi Note")
        self.outputs.new("NodeSocketStringCnt", "Name #")
        self.outputs.new("NodeSocketStringCnt", "Name b")

        self.note_update()
        super().init(context)

    def socket_update(self, socket):
        super().socket_update(socket)
        for link in socket.links:
            link.to_socket.input_value = socket.input_value
