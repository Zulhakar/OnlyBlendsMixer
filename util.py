import bpy

def get_node_tree_name(self):
    for nodegroup in bpy.data.node_groups:
        print(nodegroup.name)
        for node in nodegroup.nodes:
            print(node.name)
            if node.name == self.name:
                return nodegroup.name
    return None