import bpy

class GroupStringCollectionItem(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty()


class SoundTree(bpy.types.NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    #bl_idname = 'ObmSoundTreeType'
    bl_label = "OnlyBlends Sound Editor"
    bl_icon = 'SOUND'
    # disable internal group interface because i build it custom for more control
    bl_use_group_interface = False
    #color_tag = 'COLOR'
    parent = None
    group_node_list: bpy.props.CollectionProperty(type=GroupStringCollectionItem)
    group_node_input_list: bpy.props.CollectionProperty(type=GroupStringCollectionItem)
    group_node_output_list: bpy.props.CollectionProperty(type=GroupStringCollectionItem)

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
        print("update Node Tree:", self.bl_label)
        for link in list(self.links):
            if not link.to_node.bl_idname == "GroupNodeObm" and not link.from_node.bl_idname == "GroupNodeObm":
                #if link.to_socket.bl_idname == "GroupNodeSocket":
                if link.to_socket.bl_idname == link.from_socket.bl_idname:
                    link.is_valid = True
                if not link.is_valid:
                    print("invalid link removed:", link)
                    #self.links.remove(link)
                    print(link.to_socket.bl_idname, link.from_socket.bl_idname)
                    print(link.to_node.name, link.from_node.name)

        for node in self.nodes:
            if node.bl_idname == "NodeGroupInput":
                #print(node.name)

                for inp in node.outputs:
                    #print(inp.name)
                    has_not_input = True
                    for item in self.group_node_input_list:
                        if item.value == inp.name:
                            has_not_input = False
                    if has_not_input:
                        new_item = self.group_node_input_list.add()
                        new_item.value = inp.name
                        print("ADDED", inp.name)
                        socket_id = inp.bl_idname
                        node_names = []
                        for element in self.group_node_list:
                            node_names.append(element.value)
                        for key, value in bpy.data.node_groups.items():
                            #print(key)
                            for node_ in value.nodes:
                                if node_.name in node_names:
                                    new_sock_in_group_node = node_.inputs.new(socket_id, inp.bl_label)
                                    new_sock_in_group_node.display_shape = "LINE"
            elif node.bl_idname == "NodeGroupOutput":
                #print(node.name)
                for inp in node.inputs:
                    #print(inp.name)
                    has_not_output = True
                    for item in self.group_node_output_list:
                        if item.value == inp.name:
                            has_not_output = False
                    if has_not_output:
                        new_item = self.group_node_output_list.add()
                        new_item.value = inp.name
                        print("ADDED", inp.name)
                        socket_id = inp.bl_idname
                        node_names = []
                        for element in self.group_node_list:
                            node_names.append(element.value)
                        for key, value in bpy.data.node_groups.items():
                            #print(key)
                            for node_ in value.nodes:
                                if node_.name in node_names:
                                    new_sock_in_group_node = node_.outputs.new(socket_id,  inp.bl_label)
                                    new_sock_in_group_node.display_shape = "LINE"

            if node.bl_idname == "MY_CUSTOM_GROUP_NODE":
                node.sync_sockets()
