import bpy
from ...constants import SOUND_TREE_TYPE, IS_DEBUG
from ..basic_nodes import ObmSoundNode

class GroupNodeObm(bpy.types.NodeCustomGroup):
    #bl_idname = "GroupNodeObm"
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
        poll=lambda self, tree: (tree.bl_idname == SOUND_TREE_TYPE),
        update=lambda self, context: self.node_group_tree_update(context)
    )

    def __log(self, func_name):
        if IS_DEBUG:
            log_string = f"{self.bl_idname}-> {self.name}: {func_name} was called"
            print(log_string)

    def node_group_tree_update(self, context):
        self.__log("node_group_tree_update")


    def draw_buttons(self, context, layout):
        layout.prop(self, "all_trees", text="")

    def free(self):
        self.__log("free")
        #print("GroupNode deleted")
        #self.node_tree.group_node_list.remove(self.name)
        #for element in self.node_tree.group_node_list:
        #    print(element.value)

    def sync_sockets(self):
        self.__log("sync_sockets")

