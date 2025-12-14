import bpy

class GroupStringCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()


class GroupSocketCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    type_name: bpy.props.StringProperty()


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
            elif node.bl_idname == "NodeGroupInput":
                ids_collection = set()
                sockets_collection = []
                for item in self.group_node_input_list:
                    ids_collection.add(item.id)
                    sockets_collection.append(item)
                ids = set()
                sockets = []
                for item in node.outputs:
                    if item.bl_idname != "NodeSocketVirtual":
                        ids.add(item.identifier)
                        sockets.append(item)
                removed_ids = ids_collection - ids
                added_ids = ids - ids_collection
                is_socket_type_change = False
                if len(removed_ids) == 0 and len(added_ids) == 0:
                    for i, value in enumerate(sockets_collection):
                        if sockets_collection[i].type_name != sockets[i].bl_idname:
                            is_socket_type_change = True
                            self.sync_sockets(node)
                            sockets_collection[i].type_name = sockets[i].bl_idname
                        if sockets_collection[i].name != sockets[i].name:
                            sockets_collection[i].name = sockets[i].name
                            self.sync_sockets(node)
                if len(removed_ids) > 0:
                    remove_sockets = []
                    for i, value in enumerate(sockets):
                        if sockets_collection[i].id in removed_ids:
                            remove_sockets.append(i)
                    for remove_socket in remove_sockets:
                        self.group_node_input_list.remove(remove_socket)
                    self.sync_sockets(node)

                if len(added_ids) > 0:
                    for i, value in enumerate(sockets):
                        if sockets[i].identifier in added_ids:
                            new_item = self.group_node_input_list.add()
                            new_item.id = sockets[i].identifier
                            new_item.name = sockets[i].name
                            new_item.type_name = sockets[i].bl_idname
                    self.sync_sockets(node)
            elif node.bl_idname == "NodeGroupOutput":
                #print(node.name)
                ids_collection = set()
                sockets_collection = []
                for item in self.group_node_output_list:
                    ids_collection.add(item.id)
                    sockets_collection.append(item)
                ids = set()
                sockets = []
                for item in node.inputs:
                    if item.bl_idname != "NodeSocketVirtual":
                        ids.add(item.identifier)
                        sockets.append(item)
                removed_ids = ids_collection - ids
                added_ids = ids - ids_collection
                is_socket_type_change = False
                if len(removed_ids) == 0 and len(added_ids) == 0:
                    for i, value in enumerate(sockets_collection):
                        if sockets_collection[i].type_name != sockets[i].bl_idname:
                            is_socket_type_change = True
                            self.sync_sockets(node, False)
                            sockets_collection[i].type_name = sockets[i].bl_idname
                        if sockets_collection[i].name != sockets[i].name:
                            sockets_collection[i].name = sockets[i].name
                            self.sync_sockets(node, False)
                if len(removed_ids) > 0:
                    remove_sockets = []
                    for i, value in enumerate(sockets):
                        if sockets_collection[i].id in removed_ids:
                            remove_sockets.append(i)
                    for remove_socket in remove_sockets:
                        self.group_node_output_list.remove(remove_socket)
                    self.sync_sockets(node, False)
                if len(added_ids) > 0:
                    for i, value in enumerate(sockets):
                        if sockets[i].identifier in added_ids:
                            new_item = self.group_node_output_list.add()
                            new_item.id = sockets[i].identifier
                            new_item.name = sockets[i].name
                            new_item.type_name = sockets[i].bl_idname
                    self.sync_sockets(node, False)

    def sync_sockets(self, node, is_input=True):
        for key, value in bpy.data.node_groups.items():
            for node_ in value.nodes:
                if node_.bl_idname == "GroupNodeObm":
                    if node_.all_trees == self:
                        if is_input:
                            node_.inputs.clear()
                            for old_output in node.outputs:
                                if old_output.bl_idname != "NodeSocketVirtual":
                                    #old_output.group_node_tree_name = self.name
                                    #old_output.group_node_name = node.name
                                    node_.inputs.new(old_output.bl_idname, old_output.name)
                        else:
                            node_.outputs.clear()
                            for old_input in node.inputs:
                                if old_input.bl_idname != "NodeSocketVirtual":
                                    old_input.group_node_tree_name = node_.parent_node_tree.name
                                    old_input.group_node_name = node_.name
                                    node_.outputs.new(old_input.bl_idname, old_input.name)