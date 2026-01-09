import bpy
import aud
from ...core.global_data import on_depsgraph_update
from ...core.constants import IS_DEBUG, SOUND_SOCKET_SHAPE
from ..basic_nodes import ObmSampleNode
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


class GeometryGroupInputCollectionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    name_in_modifier: bpy.props.StringProperty()
    index: bpy.props.IntProperty()


class GeometryToSampleNode(ObmSampleNode):
    bl_idname = 'GeometryToSampleType'
    bl_label = "Geometry To Sample"

    domain_enums = [
        ('POINTCLOUD', "Point Cloud", "Use Pointcloud from geometry to create Sound Sample"),
        ('MESH', "Mesh", "Use Mesh from geometry to create Sound Sample"),

    ]
    domain: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=domain_enums
        , default='MESH'
        , update=lambda self, context: self.state_update(context))

    frequency_socket: bpy.props.EnumProperty(
        name="Frequency",
        items=lambda self, context: self.get_frequency_socket(context),
        update=lambda self, context: self.state_update(context)
    )
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

    group_input_socket_collection: bpy.props.CollectionProperty(type=GeometryGroupInputCollectionItem)

    def init(self, context):
        self.inputs.new("FloatSocketType", "Frequency")
        self.inputs.new("IntSocketType", "Sampling Rate")
        self.inputs.new("StringSocketType", "Attribute")
        self.inputs.new("IntSocketType", "Axis")
        self.inputs.new("ObjectSocketType", "Object")
        self.inputs[4].hide = True
        self.outputs.new("SoundSampleSocketType", "Sound Sample")
        self.inputs[3].input_value = 1
        self.inputs[1].input_value = 44100
        self.node_tree = None
        self.outputs[0].input_value = self.node_uuid
        bpy.context.scene.geometry_to_sample_nodes_num += 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 1:
            bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
        super().init(context)

    def get_frequency_socket(self, context):
        enums = []
        for i, item in enumerate(self.group_input_socket_collection):
            enums.append((str(i), item.name, ""))
        if len(enums) == 0:
            enums.append(("message", "No frequency socket selected", ""))
        return enums

    def state_update(self, context):
        sound_sample = self.get_sound()
        self.outputs[0].input_value = self.node_uuid
        Data.geometry_to_sample_nodes[self.node_uuid] = self
        Data.uuid_data_storage[self.node_uuid] = sound_sample
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value

    def update_node_tree(self, context):
        self.log("update_node_tree")
        if self.node_tree:
            self.obj, modifier_name = find_objects_of_node_group(self.node_tree.name)
            self.socket_update_disabled = True
            self.inputs[4].input_value = self.obj
            self.socket_update_disabled = False
            self.modifier_name = modifier_name
            modifier = self.obj.modifiers[modifier_name]
            group_input = get_group_input(self.node_tree)[0]
            i = 0
            self.group_input_socket_collection.clear()
            for key, value in modifier.items():
                if len(group_input.outputs) >= i + 1:
                    if not "_use_attribute" in key and not "_attribute_name" in key:
                        socket = group_input.outputs[i]
                        new_col_item = self.group_input_socket_collection.add()
                        new_col_item.name = socket.name
                        new_col_item.name_in_modifier = key
                        new_col_item.index = i
                        i += 1

    def __depsgraph_to_sound(self, attribute, axis, obj, sampling_rate, domain):
        print(obj)
        # bpy.context.view_layer.objects.active = obj
        depsgraph = bpy.context.view_layer.depsgraph
        track = []
        if depsgraph:
            obj_eval = depsgraph.id_eval_get(obj)
            # self.node_tree.interface.active.hide_in_modifier = True
            # self.node_tree.interface.active.hide_in_modifier = False
            geometry = obj_eval.evaluated_geometry()
            domain_data = None
            if domain == "POINTCLOUD":
                domain_data = geometry.pointcloud
            elif domain == "MESH":
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
        else:
            return None

    def get_sound(self):
        attribute = self.inputs[2].input_value
        if attribute == "":
            return None
        domain = self.domain
        sampling_rate = self.inputs[1].input_value
        axis = self.inputs[3].input_value
        return self.__depsgraph_to_sound(attribute, axis, self.obj, sampling_rate, domain)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
                layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))
        layout.prop(self, "node_tree")
        layout.prop(self, "domain", text="Domain")
        if self.node_tree:
            layout.prop(self, "frequency_socket", text="Frequency")

    def free(self):
        super().free()
        bpy.context.scene.geometry_to_sample_nodes_num -= 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 0:
            if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket != self.outputs[0] and self.modifier_name != "":
            if self.modifier_name in self.obj.modifiers:
                modifier = self.obj.modifiers[self.modifier_name]
                if len(self.group_input_socket_collection) > int(self.frequency_socket):
                    key = self.group_input_socket_collection[int(self.frequency_socket)].name_in_modifier
                    modifier[key] = self.inputs[0].input_value
                    # only to trigger change in geometry node
                    self.state_update(None)
                    self.node_tree.interface.active.hide_in_modifier = True
                    self.node_tree.interface.active.hide_in_modifier = False

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.socket_update_disabled = False

    def refresh_outputs(self):
        if IS_DEBUG:
            self.log("refresh_outputs")
        self.update_node_tree(None)
        self.state_update(None)
        bpy.context.scene.geometry_to_sample_nodes_num += 1
        if bpy.context.scene.geometry_to_sample_nodes_num == 1:
            bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)