import bpy
from ..core.constants import SOUND_TREE_TYPE



def create_child_node_tree(old_tree, selected):
    new_tree = bpy.data.node_groups.new(
        "Sound Tree",
        SOUND_TREE_TYPE
    )
    # Input / Output Nodes
    input_node = new_tree.nodes.new("NodeGroupInput")
    output_node = new_tree.nodes.new("NodeGroupOutput")
    #t = new_tree.nodes.new("TextureNodeGroup")
    # new_tree.interface.new_socket("SocketInput")

    min_x = 10000000000
    min_y = 10000000000
    max_x = -100000000000
    max_y = -100000000000
    new_names = {}
    for node in selected:
        new = new_tree.nodes.new(node.bl_idname)
        new.location = node.location
        new.copy(node)
        min_x, min_y = min(new.location.x, min_x), min(new.location.y, min_y)
        max_x, max_y = max(new.location.x, max_x), max(new.location.y, max_y)
        # mapping[node] = new
        new_names[node.name] = new.name
    if selected:
        input_node.location = (min_x - 200, min_y)
        output_node.location = (max_x + 200, min_y)
    else:
        input_node.location = (-200, 0)
        output_node.location = (200, 0)

    return new_tree, new_names, input_node, output_node

def get_index_of_socket(node, socket):
    index = 0
    for input in node.inputs:
        if input == socket:
            return index, "input"
        index += 1
    index = 0
    for output in node.outputs:
        if output == socket:
            return index, "output"
        index += 1

def get_node_by_name(tree, name):
    for node in tree.nodes:
        if node.name == name:
            return node
    return None


class NODE_OT_my_make_group(bpy.types.Operator):
    bl_idname = "node.my_make_group"
    bl_label = "My Make Group"
    bl_description = "Create a group from selected nodes (custom tree)"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR'
                and space.node_tree
                and space.node_tree.bl_idname == SOUND_TREE_TYPE)

    def execute(self, context):
        old_tree = context.space_data.node_tree
        selected = [n for n in old_tree.nodes if n.select]

        if not selected:
            self.report({'WARNING'}, "No nodes selected")
            return {'CANCELLED'}

        new_tree, new_names_dict, new_input_node, new_output_node = create_child_node_tree(old_tree, selected)

        group_node = old_tree.nodes.new("GroupNodeObm")
        group_node.node_tree = new_tree
        group_node.all_trees = new_tree
        group_node.parent_node_tree = bpy.data.node_groups[old_tree.name]
        group_node.location = selected[0].location

        new_output_node.parent = group_node
        #new_output_node["parent_group_node"] = bpy.props.PointerProperty(type=bpy.types.Node)
        #new_output_node.parent_group_node = group_node
        new_tree.parent = old_tree
        group_node.group_input_node = new_input_node.name
        group_node.group_output_node = new_output_node.name

        new_link_list = []
        group_input_socket_index = 0
        for link in old_tree.links:
            if link.from_node not in selected and link.to_node in selected:
                new_sock = new_tree.interface.new_socket(link.to_socket.bl_label, socket_type=link.to_socket.bl_idname)
                new_sock.display_shape = 'LINE'
                new_sock2 = group_node.inputs.new(link.to_socket.bl_idname, link.from_socket.bl_label)
                new_sock2.display_shape = 'LINE'
                new_link_list.append((new_sock2, link.from_socket))
                new_tree.links.new(new_input_node.outputs[group_input_socket_index],
                                   get_node_by_name(new_tree, new_names_dict[link.to_node.name]).inputs[get_index_of_socket(link.to_node, link.to_socket)[0]]).is_valid = True
                group_input_socket_index += 1
            elif link.to_node not in selected and link.from_node in selected:
                new_sock = new_tree.interface.new_socket(link.to_socket.bl_label, socket_type=link.to_socket.bl_idname, in_out="OUTPUT")
                new_sock.display_shape = 'LINE'
                new_sock2 = group_node.outputs.new(link.to_socket.bl_idname, link.to_socket.bl_label)
                new_sock2.display_shape = 'LINE'
                #new_link = old_tree.links.new(new_sock2, link.from_socket)
                new_link_list.append(( link.to_socket, new_sock2))
                new_tree.links.new(get_node_by_name(new_tree, new_names_dict[link.from_node.name]).outputs[
                                       get_index_of_socket(link.from_node, link.from_socket)[0]],
                new_output_node.inputs[get_index_of_socket(link.to_node, link.to_socket)[0]]).is_valid = True

            elif link.to_node in selected and link.from_node in selected:
                new_tree.links.new(get_node_by_name(new_tree, new_names_dict[link.from_node.name]).outputs[
                                       get_index_of_socket(link.from_node, link.from_socket)[0]],
                                   get_node_by_name(new_tree, new_names_dict[link.to_node.name]).inputs[get_index_of_socket(link.to_node, link.to_socket)[0]]).is_valid = True
        for link_tupel in new_link_list:
            old_tree.links.new(link_tupel[0], link_tupel[1]).is_valid = True


        for output in new_input_node.outputs[:-1]:
            output.display_shape = "LINE"
        for input in new_output_node.inputs[:-1]:
            input.display_shape = "LINE"
            # -----------------------------
            # inject
            input.group_node_tree_name = old_tree.name
            input.group_node_name = group_node.name

        group_name_string = new_tree.group_node_list.add()
        group_name_string.value = group_node.name
        # Optional: alte Nodes löschen
        for node in selected:
            old_tree.nodes.remove(node)

        return {'FINISHED'}


class NODE_OT_my_group_tab(bpy.types.Operator):
    bl_idname = "node.my_group_tab"
    bl_label = "Enter/Exit Group"
    bl_description = "Toggle entering/exiting a custom group node with Tab"

    @classmethod
    def poll(cls, context):
        if context.area.type != 'NODE_EDITOR':
            return False

        tree = context.space_data.node_tree
        if not tree:
            return False

        return tree.bl_idname == SOUND_TREE_TYPE


    def execute(self, context):
            space = context.space_data
            tree = space.node_tree

            #go into selected
            group_nodes = [
                n for n in tree.nodes
                if n.select and n.bl_idname == "GroupNodeObm"
            ]

            if group_nodes:
                node = group_nodes[0]
                inner = node.node_tree
                if inner:
                    space.node_tree = inner
                    return {'FINISHED'}

            #go out to parent if nothing is selected
            if hasattr(tree, "parent") and tree.parent:
                space.node_tree = tree.parent
                return {'FINISHED'}

            return {'CANCELLED'}

# "ObmSoundTreeType"

SOCKET_CHOICES = [
    ("MY_FLOAT", "Float", (0.8, 0.7, 0.2, 1.0)),
    ("MY_VECTOR", "Vector", (0.2, 0.6, 1.0, 1.0)),
    ("MY_COLOR", "Color", (0.9, 0.2, 0.5, 1.0)),
]
class MY_MT_add_interface(bpy.types.Menu):
    bl_idname = "MY_MT_add_interface"
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        layout.operator("my_interface.add_socket", text="Input").in_out = 'INPUT'
        layout.operator("my_interface.add_socket", text="Output").in_out = 'OUTPUT'



class MY_OT_AddSocket(bpy.types.Operator):
    bl_idname = "my_interface.add_socket"
    bl_label = "Add Interface Socket"

    in_out: bpy.props.EnumProperty(
        items=[
            ('INPUT', "Input", ""),
            ('OUTPUT', "Output", "")
        ]
    )

    def execute(self, context):
        tree = context.space_data.node_tree

        tree.interface.new_socket(
            name="Socket",
            socket_type="SpeakerSocketType",
            in_out=self.in_out,
        )
        if tree.parent:
            for node in tree.parent.nodes:
                print(node.name)
                print(node.bl_idname)
        return {'FINISHED'}


class MY_OT_RemoveSelected(bpy.types.Operator):
    bl_idname = "my_interface.remove_selected"
    bl_label = "Remove Selected Interface Item"

    def execute(self, context):
        tree = context.space_data.node_tree
        idx = tree.interface.active_index
        in_out = tree.interface.items_tree[idx].in_out
        print(in_out)
        num_outputs = 0
        for interface in tree.interface.items_tree:
            if interface.in_out == "OUTPUT":
                num_outputs += 1
        if 0 <= idx < len(tree.interface.items_tree):
            tree.interface.remove(tree.interface.items_tree[idx])
            if in_out == "INPUT":
                for node in tree.get_parent_group_nodes():
                    node.inputs.remove(node.inputs[idx - num_outputs])
            elif in_out == "OUTPUT":
                for node in tree.get_parent_group_nodes():
                    node.outputs.remove(node.outputs[idx])
        return {'FINISHED'}

def get_group_input(node_tree):
    inputs = []
    for node in node_tree.nodes:
        if node.bl_idname == 'NodeGroupInput':
            inputs.append(node)
    return inputs
class CUSTOM_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        #layout.prop(item, "name", text="")
        layout.template_node_view(active_data.node_tree, data, item)

class CUSTOM_UL_items2(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if item.in_out == "INPUT":
            split = layout.split(factor=0.2)
            col = item.draw_color(context, None)
            split.template_node_socket(color=col)
            split2 = split.split(factor=0.5)
            split2.label(text=item.name)
            split2.label(text="")
            #split2.template_node_socket(color=(0.0, 0.0, 0.0, 0.0))
        else:
            split = layout.split(factor=0.2)
            col = item.draw_color(context, None)
            #split.template_node_socket(color=(0.0, 0.0, 0.0, 0.0))
            split.label(text="")
            split2 = split.split(factor=0.5)
            split2.label(text=item.name)
            split2.template_node_socket(color=col)

class NODE_PT_Sound_Group_Sockets(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Group Sockets"
    bl_category = "Group"
    #bl_idname = "NODE_PT_Sound_Group_Sockets"


    @classmethod
    def poll(cls, context):
        return (
            context.space_data is not None and
            context.space_data.tree_type == SOUND_TREE_TYPE and
            context.space_data.node_tree is not None and
            context.space_data.edit_tree is not None
        )

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.node_tree

        # --- Row: List + Buttons ---
        row = layout.row()
        row.template_list(
            "CUSTOM_UL_items2",              # Blender’s builtin UIList
            "interface",                      # unique ID
            tree.interface,
            "items_tree",
            tree.interface,
            "active_index",
            rows=6,
        )

        # --- Buttons ---
        col = row.column(align=True)
        col.menu("MY_MT_add_interface", icon="ADD", text="")
        col.operator("my_interface.remove_selected", icon="REMOVE", text="")

        # --- Details for selected item ---
        idx = tree.interface.active_index
        items = tree.interface.items_tree

        if 0 <= idx < len(items):
            item = items[idx]

            if item.item_type == 'SOCKET':
                #box = layout.box()
                layout.prop(item, "name", text="Name")


                #row = box.row()
                layout.prop(item, "socket_type", text="Type")

                #layout.prop(context.scene.mysettings, "socket_style", text="Custom")

