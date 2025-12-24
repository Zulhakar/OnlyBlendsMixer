import aud
import bpy

from ..basic_nodes import ObmSampleNode
from ...core.constants import IS_DEBUG
from ...core.global_data import Data
from ...core.constants import SOUND_TREE_TYPE


def validate_node_tree(self, tree):
    input_node, output_node = _get_group_nodes(tree)
    has_sample_output = False
    has_potential_input = False
    if input_node and output_node:
        for output in input_node.outputs:
            if output.bl_idname == "FloatSocketType":
                has_potential_input = True
        for input in output_node.inputs:
            if input.bl_idname == "SoundSampleSocketType":
                has_sample_output = True
        if has_sample_output and has_potential_input:
            return True
        else:
            return False
    else:
        return False


def _get_group_nodes(tree):
    input = None
    output = None
    for node in tree.nodes:
        if node.bl_idname == "NodeGroupInput":
            input = node
        elif node.bl_idname == "NodeGroupOutput":
            output = node
    return input, output


class NodeSocketCollectionItem(bpy.types.PropertyGroup):
    # input_socket: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    # input_socket: bpy.types.NodeSocket


class NoteSequenceToSampleNode(ObmSampleNode):
    '''Select a Node Group with a Sample Output and Frequency Input. Duration is optional and can be used inside the group. If you limit the duration without the duration value from the input the Instrument Node ignore the duration of the field input'''

    bl_idname = 'NoteSequenceToSampleNodeType'
    bl_label = "Instrument"
    node_uuid: bpy.props.StringProperty()

    node_tree: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=lambda self, tree: (tree.bl_idname == SOUND_TREE_TYPE and validate_node_tree(self, tree)),
        update=lambda self, context: self.node_tree_update(context)
    )

    group_input_node: bpy.props.StringProperty()
    group_output_node: bpy.props.StringProperty()

    duration_socket: bpy.props.EnumProperty(  # type: ignore
        name="Duration"
        , items=lambda self, context: self.get_group_input_sockets(context)
        , update=lambda self, context: self.socket_selection_update(context)
        , default=-1

    )

    frequency_socket: bpy.props.EnumProperty(  # type: ignore
        name="Frequency"
        , items=lambda self, context: self.get_group_input_sockets(context)
        , update=lambda self, context: self.socket_selection_update(context)
        , default=-1

    )

    sample_output_socket: bpy.props.EnumProperty(  # type: ignore
        name="Sample"
        , items=lambda self, context: self.get_group_output_sockets(context)
        , update=lambda self, context: self.socket_selection_update(context)
        , default=-1

    )

    def get_group_input_sockets(self, context):
        socket_enums = [
            ("0", "None", "None")
        ]
        if self.node_tree:
            socket_enums = []
            group_input, group_output = _get_group_nodes(self.node_tree)
            for i, output in enumerate(group_input.outputs):
                socket_enums.append((str(i), output.name, ""))
        return socket_enums

    def get_group_output_sockets(self, context):
        socket_enums = [
            ("0", "None", "None")
        ]
        if self.node_tree:
            socket_enums = []
            group_input, group_output = _get_group_nodes(self.node_tree)
            for i, input in enumerate(group_output.inputs):
                socket_enums.append((str(i), input.name, ""))
        return socket_enums

    def socket_selection_update(self, context):
        if self.frequency_socket and self.sample_output_socket:
            self.__create_sample_sequence()

    def node_tree_update(self, context):
        self.log("node_tree_update")
        group_input, group_output = None, None
        if self.node_tree:
            group_input, group_output = _get_group_nodes(self.node_tree)
        self.group_input_node = group_input.name if group_input else ""
        self.group_output_node = group_output.name if group_output else ""

    def init(self, context):
        self.outputs.new('SoundSampleSocketType', "Sample")
        self.inputs.new("FloatVectorFieldSocketType", "Note")
        super().init(context)
        self.inputs[0].display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
            layout.label(text=self.outputs[0].input_value)

        layout.prop(self, "node_tree")
        layout.prop(self, "frequency_socket")
        layout.prop(self, "duration_socket")
        layout.prop(self, "sample_output_socket")

    def __create_sample_sequence(self):
        if len(self.inputs) >= 1 and len(
                self.outputs) >= 1 and self.node_tree and self.group_input_node != "" and self.group_output_node != "":
            input_notes_socket = self.inputs[0]
            sample = None
            if input_notes_socket.input_value and len(input_notes_socket.input_value) > 0:
                input_group = self.node_tree.nodes[self.group_input_node]
                output_group = self.node_tree.nodes[self.group_output_node]
                if int(self.frequency_socket) + 1 <= len(input_group.outputs):

                    use_duration = self.duration_socket != "" and int(self.duration_socket) + 1 <= len(
                        input_group.outputs)
                    if use_duration and isinstance(input_group.outputs[int(self.duration_socket)].input_value, float):
                        use_duration = True
                    for item in input_notes_socket.input_value:
                        frequency, duration, intensity = item.value
                        for link in input_group.outputs[int(self.frequency_socket)].links:
                            link.to_socket.input_value = frequency
                        if use_duration:
                            for link in input_group.outputs[int(self.duration_socket)].links:
                                link.to_socket.input_value = duration
                        new_sample = Data.uuid_data_storage[output_group.inputs[0].input_value]
                        new_sample = new_sample.limit(0.0, duration)
                        if sample is None:
                            sample = new_sample.volume(intensity)
                        else:
                            new_sample = new_sample.volume(intensity)
                            sample = sample.join(new_sample)

                    Data.uuid_data_storage[self.node_uuid] = sample
                    self.outputs[0].input_value = self.node_uuid

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[0]:
            self.__create_sample_sequence()
        elif socket == self.outputs[0]:
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
