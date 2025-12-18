from typing import Any

import bpy
from ..core.helper import change_socket_shape
class GroupStringCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()


class GroupSocketCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    type_name: bpy.props.StringProperty()

def get_group_input_output_nodes(tree):
    all_nodes = []
    for node in tree.nodes:
        if node.bl_idname == "NodeGroupOutput":
            all_nodes.append(node)
        elif node.bl_idname == "NodeGroupInput":
            all_nodes.append(node)
    return all_nodes

def change_all_socket_shapes(tree):
    nodes = get_group_input_output_nodes(tree)
    for node in nodes:
        change_socket_shape(node)

class SoundTree(bpy.types.NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    #bl_idname = 'ObmSoundTreeType'
    bl_label = "OnlyBlends Sound Editor"
    bl_icon = 'SOUND'
    # disable internal group interface because i build it custom for more control

    bl_use_group_interface = False
    parent: bpy.props.PointerProperty(
        name="Node Tree",
        type=bpy.types.NodeTree
    )
    group_node_list: bpy.props.CollectionProperty(type=GroupStringCollectionItem)
    group_node_input_list: bpy.props.CollectionProperty(type=GroupSocketCollectionItem)
    group_node_output_list: bpy.props.CollectionProperty(type=GroupSocketCollectionItem)

    def get_parent_group_nodes(self):
        #error if there are more than one TODO
        parent_group_nodes = []
        if self.parent:
            for node in self.parent.nodes:
                if node.bl_idname == "GroupNodeObm":
                    parent_group_nodes.append(node)
        return parent_group_nodes

    def interface_update(self, context):
        print(context)
        print("interface update")

    def update(self):
        print("update Node Tree:", self.name)
        print(str(len(self.group_node_list)))
        for link in list(self.links):
            if not link.to_node.bl_idname == "GroupNodeObm" and not link.from_node.bl_idname == "GroupNodeObm":
                #if link.to_socket.bl_idname == "GroupNodeSocket":
                if link.to_socket.bl_idname == link.from_socket.bl_idname:
                    link.is_valid = True
                if not link.is_valid:
                    print("invalid link removed:", link)
                    self.links.remove(link)
                    print(link.to_socket.bl_idname, link.from_socket.bl_idname)
                    print(link.to_node.name, link.from_node.name)

        for node in self.nodes:
            if node.bl_idname == "GroupNodeObm":
                node.parent_node_tree = self
                print(node.name)
                is_in_list = False
                for key, value in self.group_node_list.items():
                    if value.name == node.name:
                        is_in_list = True
                if not is_in_list:
                    print("add new group node")
                    new_group_node_item = self.group_node_list.add()
                    new_group_node_item.name = node.name
                    new_group_node_item.id = node.name
                    print(str(len(self.group_node_list)))
            elif node.bl_idname == "NodeGroupOutput":
                #add reference to socket for group output update
                for inp_sock in node.inputs:
                    if inp_sock.bl_idname != "NodeSocketVirtual":
                        if self.parent:
                            inp_sock.selected_node_group_name = self.parent.name
                        inp_sock.node_group_name = self.name

        inputs = []
        outputs = []
        for interface in self.interface.items_tree:
            if hasattr(interface, "in_out"):
                if interface.in_out == 'INPUT':
                    inputs.append(interface)
                elif interface.in_out == 'OUTPUT':
                    outputs.append(interface)
        

        self.handle_socks(inputs, True)
        self.handle_socks(outputs, False)

    
    def handle_socks(self, sockets: list[Any], are_inputs=True):


        ids_collection = set()
        sockets_collection = []
        if are_inputs:
            group_node_in_out_list = self.group_node_input_list
        else:
            group_node_in_out_list = self.group_node_output_list
        if len(sockets) == 0:
            #group_node_in_out_list.clear()
            self.sync_sockets(sockets, are_inputs)
        else:
            for item in group_node_in_out_list:
                ids_collection.add(item.id)
                sockets_collection.append(item)
            ids = set()
            sockets_tmp = []
            for item in sockets:
                if item.bl_socket_idname != "NodeSocketVirtual":
                    ids.add(item.identifier)
                    sockets_tmp.append(item)
            removed_ids = ids_collection - ids
            added_ids = ids - ids_collection
            if len(removed_ids) == 0 and len(added_ids) == 0:
                for i, value in enumerate(sockets_collection):
                    if sockets_collection[i].type_name != sockets_tmp[i].bl_socket_idname:
                        self.sync_sockets(sockets, are_inputs)
                        change_all_socket_shapes(self)
                        sockets_collection[i].type_name = sockets_tmp[i].bl_socket_idname
                    if sockets_collection[i].name != sockets_tmp[i].name:
                        sockets_collection[i].name = sockets_tmp[i].name
                        self.sync_sockets(sockets, are_inputs)
                        change_all_socket_shapes(self)

            if len(removed_ids) > 0:
                remove_sockets = []
                for i, value in enumerate(sockets_tmp):
                    if sockets_collection[i].id in removed_ids:
                        remove_sockets.append(i)
                for remove_socket in remove_sockets:
                    group_node_in_out_list.remove(remove_socket)
                self.sync_sockets(sockets, are_inputs)
                change_all_socket_shapes(self)

            if len(added_ids) > 0:
                for i, value in enumerate(sockets_tmp):
                    if sockets_tmp[i].identifier in added_ids:
                        new_item = group_node_in_out_list.add()
                        new_item.id = sockets_tmp[i].identifier
                        new_item.name = sockets_tmp[i].name
                        new_item.type_name = sockets_tmp[i].bl_socket_idname
                self.sync_sockets(sockets, are_inputs)
                change_all_socket_shapes(self)

    def sync_sockets(self, sockets, is_input=True):
        for key, value in bpy.data.node_groups.items():
            for node_ in value.nodes:
                if node_.bl_idname == "GroupNodeObm":
                    if node_.all_trees == self:
                        if is_input:
                            node_.inputs.clear()
                            for old_output in sockets:
                                if old_output.bl_socket_idname != "NodeSocketVirtual":
                                    old_output.selected_node_group_name = node_.parent_node_tree.name
                                    old_output.node_group_name = node_.name
                                    node_.inputs.new(old_output.bl_socket_idname, old_output.name)
                                    change_socket_shape(node_)

                        else:
                            node_.outputs.clear()
                            for old_input in sockets:
                                if old_input.bl_socket_idname != "NodeSocketVirtual":
                                    old_input.selected_node_group_name = node_.parent_node_tree.name
                                    old_input.node_group_name = node_.name
                                    node_.outputs.new(old_input.bl_socket_idname, old_input.name)
                                    change_socket_shape(node_)
