import bpy
import aud
from ...core.global_data import on_depsgraph_update
from ...core.constants import IS_DEBUG, SOUND_SOCKET_SHAPE
from ..basic_nodes import ObmSoundNode
from ...core.global_data import Data
import uuid
import numpy as np



def find_objects_of_node_group(target_node_group_name):

    found_objects = []

    # Iterate through all objects in the current blend file
    for obj in bpy.data.objects:
        # Iterate through all modifiers on the object
        for mod in obj.modifiers:
            # Check if the modifier is a Geometry Nodes modifier ('NODES')
            if mod.type == 'NODES':
                # Check if the node group assigned to the modifier matches the target name
                if mod.node_group and mod.node_group.name == target_node_group_name:
                    found_objects.append((obj, mod.name))
                    # Optional: Break to avoid adding the same object multiple times
                    # if it uses the group in multiple modifiers
                    break

    return found_objects[0]

def get_group_input(node_tree):
    inputs = []
    for node in node_tree.nodes:
        if node.bl_idname == 'NodeGroupInput':
            inputs.append(node)
    return inputs

class CUSTOM_UL_geometry_group_input_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        group_input = get_group_input(active_data.node_tree)[0]
        layout.template_node_socket(color=group_input.outputs[item.index].draw_color_simple())
        layout.label(text=item.name)


class GeometryGroupInputCollectionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    name_in_modifier: bpy.props.StringProperty()
    index: bpy.props.IntProperty()


class GeometryToSampleNode(ObmSoundNode, bpy.types.Node):
    bl_idname = 'GeometryToSampleType'
    bl_label = "Geometry To Sample"

    node_uuid: bpy.props.StringProperty()

    operations = [
        ('POINTCLOUD', "Pointcloud", "Use Pointcloud from geometry to create Sound Sample"),
        ('MESH', "Mesh", "Use Mesh from geometry to create Sound Sample"),

    ]
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations
        , default='MESH'
        , update=lambda self, context: self.operation_update())

    node_tree: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=lambda self, tree: (tree.bl_idname == "GeometryNodeTree" and tree.is_modifier),
        update=lambda self, context: self.update_node_tree(context)
    )
    obj: bpy.props.PointerProperty(
        type=bpy.types.Object
    )
    modifier_name: bpy.props.StringProperty()
    selected_socket_index: bpy.props.IntProperty()
    group_input_socket_collection: bpy.props.CollectionProperty(type=GeometryGroupInputCollectionItem)

    def init(self, context):
        #self.inputs.new("ObjectSocketType", "Object")
        self.inputs.new("StringSocketType", "Attribute")
        self.inputs.new("IntSocketType", "Axis")
        self.inputs.new("IntSocketType", "Sampling Rate")
        self.inputs.new("FloatSocketType", "Frequency")
        self.outputs.new("SoundSampleSocketType", "Sound Sample")
        self.inputs[1].input_value = 1
        self.inputs[2].input_value = 44100

        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        # if len(bpy.data.node_groups) > 0:
        #     self.node_tree = bpy.data.node_groups[0]
        #     for node in bpy.data.node_groups:
        #         if node.bl_idname == "GeometryNodeTree" and node.is_modifier:
        #             self.node_tree = node
        self.node_tree = None
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        self.outputs[0].input_value = self.node_uuid
        Data.uuid_data_storage[self.node_uuid] = aud.Sound.silence(44100).limit(0, 0.2)
        Data.geometry_to_sample_nodes[self.node_uuid] = self

        bpy.context.scene.geometry_to_sample_nodes_num += 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 1:

            bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
        self.selected_socket_index = 0
    def operation_update(self):
        sound_sample = self.get_sound()
        Data.geometry_to_sample_nodes[self.node_uuid] = self
        Data.uuid_data_storage[self.node_uuid] = sound_sample

        for link in self.outputs[0].links:
            link.to_node.update_obm()

    def update_node_tree(self, context):
        self.log("update_node_tree")
        if self.node_tree:
            self.obj, modifier_name = find_objects_of_node_group(self.node_tree.name)
            self.modifier_name = modifier_name
            modifier = self.obj.modifiers[modifier_name]
            #print(modifier.name)
            group_input = get_group_input(self.node_tree)[0]
            i = 0
            for key, value in modifier.items():
                if len(group_input.outputs) >= i+1:
                    if not "_use_attribute" in key and not "_attribute_name" in key:
                        socket = group_input.outputs[i]
                        new_col_item = self.group_input_socket_collection.add()
                        new_col_item.name = socket.name
                        print(socket.name)
                        print(key)
                        print(value)
                        new_col_item.name_in_modifier = key
                        new_col_item.index = i
                        i += 1
            #    if isinstance(value, float):
            #        modifier[key] = 111.0
            #self.node_tree.interface.active.hide_in_modifier = True


    def __depsgraph_to_sound(self, attribute, axis, obj, sampling_rate, option):
        depsgraph = bpy.context.view_layer.depsgraph
        track = []
        obj_eval = depsgraph.id_eval_get(obj)
        geometry = obj_eval.evaluated_geometry()
        domain_data = None
        if option == "POINTCLOUD":
            domain_data = geometry.pointcloud
        elif option == "MESH":
            domain_data = geometry.mesh
        if domain_data is None:
            return None
        if attribute not in domain_data.attributes:
            return None
        attr_data = domain_data.attributes[attribute].data
        length_of_data = len(attr_data)
        duration = length_of_data / sampling_rate
        for vert in attr_data:
            v = vert.vector
            v_tup = tuple(v)
            track.append(v_tup[axis])
        sound_array = np.asarray([track]).T.astype(np.float32)
        sound_sample = aud.Sound.buffer(sound_array, sampling_rate)
        return sound_sample

    def get_sound(self):
        attribute = self.inputs[0].input_value
        if attribute == "":
            return None
        option = self.operation
        sampling_rate = self.inputs[2].input_value
        axis = self.inputs[1].input_value
        return self.__depsgraph_to_sound(attribute, axis, self.obj, sampling_rate, option)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
        layout.prop(self, "node_tree")
        layout.prop(self, "operation", text="Operation")
        #if self.inputs[0].input_value:
        if self.node_tree:
            layout.template_list(
                "CUSTOM_UL_geometry_group_input_items",  # Blender’s builtin UIList
                "the_unique_list",  # unique ID
                self,
                "group_input_socket_collection",
                self,
                "selected_socket_index",
                rows=1,
                maxrows=1,#type="COMPACT"
            )
            #men_ref = layout.menu("MY_MT_CustomDropdown", text=self.group_input_socket_collection[self.selected_socket_index].name)
            #men_ref.group_input_socket_collection = self.group_input_socket_collection
            #men_ref.active_item = self.selected_socket_index

    def free(self):
        super().free()
        bpy.context.scene.geometry_to_sample_nodes_num -= 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 0:
            bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket == self.inputs[3]:

            modifier = self.obj.modifiers[self.modifier_name]
            #for key, value in modifier.items():
            #    if isinstance(value, float):
            #        modifier[key] = socket.input_value
            #self.node_tree.interface.active.hide_in_modifier = True

            key = self.group_input_socket_collection[self.selected_socket_index].name_in_modifier
            modifier[key] = socket.input_value
            self.node_tree.interface.active.hide_in_modifier = True