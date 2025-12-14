import bpy

from ...core.constants import SOUND_TREE_TYPE
from ...nodes.basic_nodes import ObmConstantNode
from ...core.helper import get_socket_index, _checker


class GroupNodeObm(ObmConstantNode):
    bl_label = "Sound Group"
    bl_icon = 'NODETREE'
    node_tree: bpy.props.PointerProperty(
        name="Group Tree",
        type=bpy.types.NodeTree,
        update=lambda self, context: self.sync_sockets()
    )

    all_trees: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=lambda self, tree: (tree.bl_idname == SOUND_TREE_TYPE and _checker(self, tree)),
        update=lambda self, context: self.node_group_tree_update(context)
    )

    parent_node_tree: bpy.props.PointerProperty(
        name="Node Tree",
        type=bpy.types.NodeTree
    )

    group_input_node : bpy.props.StringProperty()
    group_output_node :  bpy.props.StringProperty()

    def init(self, context):
        super().init(context)

    def node_group_tree_update(self, context):
        self.log("node_group_tree_update")
        self.all_trees.group_node_input_list.clear()
        self.all_trees.group_node_output_list.clear()
        self.all_trees.update()

        #self.parent_node_tree.update()
        #self.parent_node_tree.update()
    def draw_buttons(self, context, layout):
        layout.prop(self, "all_trees", text="")

    def sync_sockets(self):
        self.log("sync_sockets")

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket.name in self.inputs:
            input_group = None
            output_group = None
            if self.node_tree:
                if self.group_input_node:
                    input_group = self.node_tree.nodes[self.group_input_node]
                if self.group_output_node:
                    output_group = self.node_tree.nodes[self.group_output_node]
            if input_group:
                index = get_socket_index(self.inputs, socket)
                input_group.outputs[index].input_value = socket.input_value
                for link in input_group.outputs[index].links:
                    link.to_socket.input_value = socket.input_value
                print("CASSCADE END")