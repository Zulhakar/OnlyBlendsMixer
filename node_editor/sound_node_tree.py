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
    #color_tag = 'COLOR'
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
                #print(node.name)
                for inp in node.outputs:
                    #print(inp.name)
                    has_not_input = True
                    socket_type_change = False
                    for item in self.group_node_input_list:
                        if item.id == inp.identifier:
                            has_not_input = False
                            if item.type_name != inp.bl_idname:
                                socket_type_change = True
                                self.synck_sockets(node)
                                item.type_name = inp.bl_idname
                                print(item.type_name)

                    if socket_type_change:
                        print("socket_type_change")

                    if has_not_input:
                        new_item = self.group_node_input_list.add()
                        new_item.id = inp.identifier
                        new_item.name = inp.name
                        new_item.type_name = inp.bl_idname
                        print("ADDED", inp.name)
                        if inp.name == "":
                            print("group input added")
                        else:
                            socket_id = inp.bl_idname
                            for key, value in bpy.data.node_groups.items():
                                for node_ in value.nodes:
                                    if node_.bl_idname == "GroupNodeObm":
                                        if node_.all_trees == self:
                                            new_sock_in_group_node = node_.inputs.new(socket_id, inp.bl_label)
                                            new_sock_in_group_node.display_shape = "LINE"


            elif node.bl_idname == "NodeGroupOutput":
                #print(node.name)
                for inp in node.inputs:
                    #print(inp.name)
                    has_not_output = True
                    for item in self.group_node_output_list:
                        if item.id == inp.identifier:
                            has_not_output = False
                            if item.type_name != inp.bl_idname:
                                socket_type_change = False
                                self.synck_sockets(node, False)
                                item.type_name = inp.bl_idname
                                print(item.type_name)
                    if has_not_output:
                        new_item = self.group_node_output_list.add()
                        new_item.id = inp.identifier
                        new_item.name = inp.name
                        new_item.type_name = inp.bl_idname
                        print("ADDED", inp.name)
                        if inp.name == "":
                            print("group output added")
                        else:
                            socket_id = inp.bl_idname
                            for key, value in bpy.data.node_groups.items():
                                for node_ in value.nodes:
                                    if node_.bl_idname == "GroupNodeObm":
                                        if node_.all_trees == self:
                                            new_sock_in_group_node = node_.outputs.new(socket_id, inp.bl_label)
                                            new_sock_in_group_node.display_shape = "LINE"

    def synck_sockets(self, node, is_input=True):
        for key, value in bpy.data.node_groups.items():
            for node_ in value.nodes:
                if node_.bl_idname == "GroupNodeObm":
                    if node_.all_trees == self:
                        if is_input:
                            node_.inputs.clear()
                            for old_output in node.outputs:
                                if old_output.bl_idname != "NodeSocketVirtual":
                                    node_.inputs.new(old_output.bl_idname, old_output.name)
                        else:
                            node_.outputs.clear()
                            for old_input in node.inputs:
                                if old_input.bl_idname != "NodeSocketVirtual":
                                    node_.outputs.new(old_input.bl_idname, old_input.name)

