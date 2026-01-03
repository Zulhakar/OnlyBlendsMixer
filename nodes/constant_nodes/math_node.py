import bpy

from ..basic_nodes import ObmConstantNode
from ...core.constants import IS_DEBUG


class MathNode(ObmConstantNode):
    '''Basic Math operations'''
    bl_label = "Math"

    operations_enums = (
        ('ADD', 'Add', 'Add'),
        ('SUB', 'Subtract', 'Subtract'),
        ('MUL', 'Multiply', 'Multiply'),
        ('DIV', 'Divide', 'Divide')
    )
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations_enums
        , default="ADD"
        , update=lambda self, context: self.operation_update())

    def operation_update(self):
        if self.operation == "ADD":
            self.outputs[0].input_value = (self.inputs[0].input_value + self.inputs[1].input_value)
        elif self.operation == "SUB":
            self.outputs[0].input_value = (self.inputs[0].input_value - self.inputs[1].input_value)
        elif self.operation == "MUL":
            self.outputs[0].input_value = (self.inputs[0].input_value * self.inputs[1].input_value)
        elif self.operation == "DIV":
            if self.inputs[1].input_value == 0.0:
                import sys
                self.outputs[0].input_value = sys.float_info.max
            else:
                self.outputs[0].input_value = (self.inputs[0].input_value / self.inputs[1].input_value)
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            if len(self.outputs) > 0:
                layout.label(text=f"input1: {self.inputs[0].input_value}")
                layout.label(text=f"input2: {self.inputs[1].input_value}")
                layout.label(text=f"output: {self.outputs[0].input_value}")
        layout.prop(self, "operation", text="")

    def init(self, context):
        self.inputs.new('FloatSocketType', "Float")
        self.inputs.new('FloatSocketType', "Float")
        self.outputs.new('FloatSocketType', "Float")
        super().init(context)

    def socket_update(self, socket):
        if socket != self.outputs[0]:
            self.operation_update()

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.operation = node.operation
        self.socket_update_disabled = False