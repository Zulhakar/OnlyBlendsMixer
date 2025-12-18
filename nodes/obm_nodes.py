import bpy
import uuid
import aud
import numpy as np

from ..core.constants import SAMPLE_TO_GEOMETRY_NODE_DESCRIPTION, SAMPLE_TO_MESH_NODE_DESCRIPTION
from .basic_nodes import ObmSoundNode
from ..sockets.basic_sockets import SoundSocket
from ..core.constants import SOUND_SOCKET_SHAPE, IS_DEBUG, DEVICE_SOCKET_SHAPE
from ..sockets.basic_sockets import SoundSampleSocket
from ..core.global_data import Data


class ImportWavNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    bl_idname = 'ImportWavNodeType'
    bl_label = "Import WAV"
    import_path: bpy.props.StringProperty(update=lambda self, context: self.__update_import_path())
    node_uuid: bpy.props.StringProperty()

    header_color: bpy.props.FloatVectorProperty(
        name="Header Color",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        default=(0.0, 0.0, 0.09)
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, "header_color")

    def init(self, context):
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.create_import_wave_panel(self, uuid_tmp)
        self.inputs.new("WavImportSocketType", "Wave File")
        self.outputs.new('SoundSocketType', "Sound")
        # self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

    def free(self):
        if self.node_uuid in Data.uuid_operator_class_storage:
            bpy.utils.unregister_class(Data.uuid_operator_class_storage[self.node_uuid])

    def __update_import_path(self):
        print("__update_import_path")
        self.inputs[0].input_value = self.import_path
        args = {"filepath": self.import_path}

        # sound datablock which can also be used with speaker
        result = bpy.ops.sound.open(**args)

        # from pathlib import Path
        # file_name = Path(self.filepath).name
        # print(file_name)
        last = None
        sound = None
        for s in bpy.data.sounds:
            if s.filepath == self.import_path:
                last = s
                sound = bpy.types.BlendDataSounds(last)
        self.outputs[0].input_value = sound
        print(sound)
        device = aud.Device()
        aud_sound = aud.Sound.file(self.import_path)
        handle2 = device.play(aud_sound)


class SoundInfoNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Sound from an object'''

    bl_idname = 'SoundInfoNodeType'
    bl_label = "Sound Info"

    def init(self, context):
        self.inputs.new('SoundSocketType', "Sound")
        self.outputs.new('NodeSocketString', "Path")
        self.outputs.new('NodeSocketString', "Blender Path")
        self.outputs.new('NodeSocketString', "Channels")
        self.outputs.new('NodeSocketInt', "Sample Rate")
        # self.outputs[0].display_shape = SOUND_SOCKET_SHAPE

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Infos")
        # r = layout.row()
        # r.prop(self, 'import_path', text="")
        layout.label(text="Path: " + self.outputs[0].default_value)
        layout.label(text="Blender Path: " + self.outputs[1].default_value)
        layout.label(text="Channels: " + self.outputs[2].default_value)
        layout.label(text="Samplerate: " + str(self.outputs[3].default_value))
        # r.label(text="Path: " + self.outputs[0].default_value)

    def refresh_outputs(self):
        self.outputs[0].default_value = self.inputs[0].input_value.filepath
        self.outputs[1].default_value = self.inputs[0].input_value.name_full
        self.outputs[2].default_value = self.inputs[0].input_value.channels
        self.outputs[3].default_value = self.inputs[0].input_value.samplerate

    def draw_label(self):
        return "Sound Info"

    def insert_link(self, link):
        print("link")
        print(link)
        s = link.from_socket.input_value
        self.inputs[0].input_value = link.from_socket.input_value
        self.refresh_outputs()

    def update(self):
        # This method is called when the node updates
        print("update Sound Info")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        if isinstance(socket, SoundSocket):
            print("Sound Socket")
            if not self.inputs[0].is_linked:
                if self.inputs[0].input_value is not None:
                    self.refresh_outputs()


class SoundToSampleNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Sound Sample  which can be modified, played and recorded'''

    bl_idname = 'SoundToSampleNodeType'
    bl_label = "Sound To Sample"
    # update=lambda self, context: self.update_sound_prop(),
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.inputs.new('SoundSocketType', "Sound")
        self.outputs.new('SoundSampleSocketType', "Sound Sample")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Infos")
        layout.label(text=self.outputs[0].input_value)
        if self.node_uuid in Data.uuid_data_storage and Data.uuid_data_storage[self.node_uuid] is not None:
            layout.label(text="Duration: " + str(Data.uuid_data_storage[self.node_uuid].length))


    def refresh_outputs(self):
        print("refresh outputs")
        if self.inputs[0].input_value is not None:
            Data.uuid_data_storage[self.node_uuid] = aud.Sound.file(self.inputs[0].input_value.filepath)
            self.outputs[0].input_value = self.node_uuid

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        print(link)
        s = link.from_socket.input_value
        # insert into logic
        if isinstance(link.from_socket, SoundSocket):
            self.inputs[0].input_value = link.from_socket.input_value
            self.refresh_outputs()

    def update(self):
        # This method is called when the node updates
        print("update Sound Info")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        if isinstance(socket, SoundSocket):
            print("Sound Socket")
            if not self.inputs[0].is_linked:
                if self.inputs[0].input_value is None:
                    Data.uuid_data_storage[self.node_uuid] = None
                else:
                    self.refresh_outputs()


class CreateDeviceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''A Device To Play Sound Samples'''

    bl_idname = 'CreateDeviceNodeType'
    bl_label = "Create Sound Device"
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.outputs.new('DeviceSocketType', "Device")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs.new('FloatSocketType', 'Volume')
        self.inputs[0].input_value = 1.0
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        self.create_device()
        self.outputs[0].input_value = uuid_tmp

    def create_device(self):
        device = aud.Device()
        device.volume = self.inputs[0].input_value
        Data.uuid_data_storage[self.node_uuid] = device

    def refresh_outputs(self):
        if self.node_uuid is not None and self.node_uuid != "":
            if self.node_uuid not in Data.uuid_data_storage:
                self.create_device()

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.node_uuid in Data.uuid_data_storage.keys():
                layout.label(text="Volume: " + str(Data.uuid_data_storage[self.node_uuid].volume))

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        link.to_socket.input_value = link.from_socket.input_value
        self.create_device()

    def update(self):
        # This method is called when the node updates
        print("update Device Node")

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update")
        print(socket)
        self.create_device()


class PlayDeviceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''A Device To Play Sound Samples on specific frame. Animatable'''

    bl_idname = 'PlayDeviceNodeType'
    bl_label = "Play Device"

    def init(self, context):
        self.inputs.new('DeviceSocketType', "Device")
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs[0].display_shape = DEVICE_SOCKET_SHAPE
        self.inputs[1].display_shape = SOUND_SOCKET_SHAPE
        dummy = bpy.context.scene.samples.add()
        dummy.node_name = self.name
        dummy.is_played = False

    def free(self):
        super().free()
        prop = self.get_ext_prop()
        bpy.context.scene.samples.remove(prop)
        for sample in bpy.context.scene.samples:
            print(sample)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.inputs[1].input_value is None:
                layout.label(text="Duration: " + str(self.inputs[1].input_value.length))
        layout.prop(self.get_ext_prop(), 'is_played')

    def insert_link(self, link):
        super().insert_link(link)
        link.to_socket.input_value = link.from_socket.input_value
        prop = self.get_ext_prop()
        prop.sample_uuid = self.inputs[1].input_value
        prop.device_uuid = self.inputs[0].input_value

    def get_ext_prop(self):
        final_prop = None
        for prop in bpy.context.scene.samples:
            if prop.node_name == self.name:
                final_prop = prop
                return final_prop
        return final_prop


class PLAY_DEVICE_OT_actions(bpy.types.Operator):
    """Play Device"""
    bl_idname = "obm.device_action_op"
    bl_label = "Device Actions"
    bl_description = "Play Device"
    bl_options = {'REGISTER'}

    sample_uuid: bpy.props.StringProperty()

    device_uuid: bpy.props.StringProperty()

    action: bpy.props.StringProperty()

    def invoke(self, context, event):
        info = "test info"
        self.report({'INFO'}, info)
        sound = Data.uuid_data_storage[self.sample_uuid]
        device = Data.uuid_data_storage[self.device_uuid]
        if self.action == "PLAY":
            handle = device.play(sound)
        elif self.action == "STOP_ALL":
            handle = device.stopAll()
        return {"FINISHED"}


class PLAY_DEVICE_OT_actions2(bpy.types.Operator):
    """Play Device"""
    bl_idname = "obm.device_action2_op"
    bl_label = "Device Actions"
    bl_description = "Play Device"
    bl_options = {'REGISTER'}

    sample_uuid: bpy.props.StringProperty()

    device_uuid: bpy.props.StringProperty()

    action: bpy.props.StringProperty()

    handle: None

    def execute(self, context):
        print("execute")
        sound = Data.uuid_data_storage[self.sample_uuid]
        device = Data.uuid_data_storage[self.device_uuid]
        if self.action == "PLAY":
            self.handle = device.play(sound)
            return {'FINISHED'}
        elif self.action == "STOP_ALL":
            self.handle = device.stopAll()
            return {"FINISHED"}
        return {"FINISHED"}


class DeviceActionNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''A Device To Play Sound Samples on specific frame. Animatable'''

    # operator siehe gateway entry
    bl_idname = 'DeviceActionNodeType'
    bl_label = "Device Actions"

    def init(self, context):
        self.inputs.new('DeviceSocketType', "Device")
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.inputs[0].display_shape = DEVICE_SOCKET_SHAPE
        self.inputs[1].display_shape = SOUND_SOCKET_SHAPE

    def free(self):
        super().free()
        if self.inputs[0].input_value != "":
            device = Data.uuid_data_storage[self.device_uuid]
            device.stopAll()

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Debug Infos:")
            if self.inputs[1].input_value is None:
                layout.label(text="Duration: " + str(self.inputs[1].input_value.length))

        row = layout.row()
        op = row.operator("obm.device_action2_op", icon='PLAY', text="")
        op.device_uuid = self.inputs[0].input_value
        op.sample_uuid = self.inputs[1].input_value
        op.action = "PLAY"
        if hasattr(op, "handle"):
            if op.handle is not None:
                row.label(text=op.handle.status)
        op2 = row.operator("obm.device_action2_op", icon='KEY_EMPTY1_FILLED', text="")
        op2.device_uuid = self.inputs[0].input_value
        op2.sample_uuid = self.inputs[1].input_value
        op2.action = "STOP_ALL"

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.bl_idname != link.from_socket.bl_idname:
            print("error")
        else:
            link.to_socket.input_value = link.from_socket.input_value


class EditDeviceNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''A Device To Play Sound Samples'''

    bl_idname = 'EditDeviceNodeType'
    bl_label = "Edit Sound Device"
    node_uuid: bpy.props.StringProperty()

    def init(self, context):
        self.outputs.new('DeviceSocketType', "Device")
        self.inputs.new('DeviceSocketType', "Device")
        self.outputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE
        self.inputs.new('FloatSocketType', 'Volume')
        self.inputs[0].input_value = 1.0
        uuid_tmp = str(uuid.uuid4()).replace("-", "")
        self.node_uuid = uuid_tmp
        Data.uuid_data_storage[self.node_uuid] = aud.Device()
        Data.uuid_data_storage[self.node_uuid].volume = 1.0
        self.outputs[0].input_value = uuid_tmp

    def create_device(self):
        device = aud.Device()
        device.volume = self.inputs[0].input_value
        Data.uuid_data_storage[self.node_uuid] = device

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        super().copy(node)

    # Free function to clean up on removal.
    def free(self):
        super().free()
        del Data.uuid_data_storage[self.node_uuid]

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Debug Infos:")
        if self.node_uuid in Data.uuid_data_storage.keys():
            layout.label(text="Volume: " + str(Data.uuid_data_storage[self.node_uuid].volume))

    def insert_link(self, link):
        super().insert_link(link)
        link.to_socket.input_value = link.from_socket.input_value
        self.create_device()

    def socket_update(self, socket):
        super().socket_update(socket)
        self.create_device()






def point_cloud_from_mesh_gn_node_group(name):
    point_cloud_from_mesh_gn = bpy.data.node_groups.new(type='GeometryNodeTree', name=name)

    point_cloud_from_mesh_gn.color_tag = 'NONE'
    point_cloud_from_mesh_gn.description = ""
    point_cloud_from_mesh_gn.default_group_node_width = 140

    point_cloud_from_mesh_gn.is_modifier = True

    # point_cloud_from_mesh_gn interface
    # Socket Geometry
    geometry_socket = point_cloud_from_mesh_gn.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                                    socket_type='NodeSocketGeometry')
    geometry_socket.attribute_domain = 'POINT'
    geometry_socket.default_input = 'VALUE'
    geometry_socket.structure_type = 'AUTO'

    # Socket Geometry
    geometry_socket_1 = point_cloud_from_mesh_gn.interface.new_socket(name="Geometry", in_out='INPUT',
                                                                      socket_type='NodeSocketGeometry')
    geometry_socket_1.attribute_domain = 'POINT'
    geometry_socket_1.default_input = 'VALUE'
    geometry_socket_1.structure_type = 'AUTO'

    # Socket Count
    count_socket = point_cloud_from_mesh_gn.interface.new_socket(name="Count", in_out='INPUT',
                                                                 socket_type='NodeSocketInt')
    count_socket.default_value = 10
    count_socket.min_value = 0
    count_socket.max_value = 2147483647
    count_socket.subtype = 'NONE'
    count_socket.attribute_domain = 'POINT'
    count_socket.description = "The number of points to create"
    count_socket.default_input = 'VALUE'
    count_socket.structure_type = 'AUTO'

    # initialize point_cloud_from_mesh_gn nodes
    # node Group Input
    group_input = point_cloud_from_mesh_gn.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"

    # node Group Output
    group_output = point_cloud_from_mesh_gn.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.is_active_output = True

    # node Points
    points = point_cloud_from_mesh_gn.nodes.new("GeometryNodePoints")
    points.name = "Points"
    # Radius
    points.inputs[2].default_value = 9.999999747378752e-06

    # node Position
    position = point_cloud_from_mesh_gn.nodes.new("GeometryNodeInputPosition")
    position.name = "Position"

    # node Sample Index
    sample_index = point_cloud_from_mesh_gn.nodes.new("GeometryNodeSampleIndex")
    sample_index.name = "Sample Index"
    sample_index.clamp = False
    sample_index.data_type = 'FLOAT_VECTOR'
    sample_index.domain = 'POINT'

    # node Index
    index = point_cloud_from_mesh_gn.nodes.new("GeometryNodeInputIndex")
    index.name = "Index"

    # node Domain Size
    domain_size = point_cloud_from_mesh_gn.nodes.new("GeometryNodeAttributeDomainSize")
    domain_size.name = "Domain Size"
    domain_size.component = 'MESH'

    # Set locations
    group_input.location = (-685.3740844726562, 166.578857421875)
    group_output.location = (156.9349822998047, 410.7016296386719)
    points.location = (-62.33095932006836, 563.706298828125)
    position.location = (-557.9932861328125, 430.3790588378906)
    sample_index.location = (-222.2251434326172, 328.3319396972656)
    index.location = (-651.409423828125, 356.1745300292969)
    domain_size.location = (-331.29730224609375, 631.0365600585938)

    # Set dimensions
    group_input.width, group_input.height = 140.0, 100.0
    group_output.width, group_output.height = 140.0, 100.0
    points.width, points.height = 140.0, 100.0
    position.width, position.height = 140.0, 100.0
    sample_index.width, sample_index.height = 140.0, 100.0
    index.width, index.height = 140.0, 100.0
    domain_size.width, domain_size.height = 140.0, 100.0

    # initialize point_cloud_from_mesh_gn links
    # points.Points -> group_output.Geometry
    point_cloud_from_mesh_gn.links.new(points.outputs[0], group_output.inputs[0])
    # group_input.Geometry -> sample_index.Geometry
    point_cloud_from_mesh_gn.links.new(group_input.outputs[0], sample_index.inputs[0])
    # position.Position -> sample_index.Value
    point_cloud_from_mesh_gn.links.new(position.outputs[0], sample_index.inputs[1])
    # sample_index.Value -> points.Position
    point_cloud_from_mesh_gn.links.new(sample_index.outputs[0], points.inputs[1])
    # index.Index -> sample_index.Index
    point_cloud_from_mesh_gn.links.new(index.outputs[0], sample_index.inputs[2])
    # domain_size.Point Count -> points.Count
    point_cloud_from_mesh_gn.links.new(domain_size.outputs[0], points.inputs[0])
    # group_input.Geometry -> domain_size.Geometry
    point_cloud_from_mesh_gn.links.new(group_input.outputs[0], domain_size.inputs[0])
    return point_cloud_from_mesh_gn



class SampleInfoNode(ObmSoundNode, bpy.types.NodeCustomGroup):
    '''Infos of Sound Sample'''
    bl_idname = 'SampleInfoNodeType'
    bl_label = "Sample Info"

    def init(self, context):
        self.inputs.new('SoundSampleSocketType', "Sound Sample")
        self.outputs.new("IntSocketType", "Sample Num")
        self.outputs.new("FloatSocketType", "Duration")
        self.outputs.new("IntSocketType", "Sample Rate")
        self.outputs.new("IntSocketType", "Channels")
        self.inputs[0].display_shape = SOUND_SOCKET_SHAPE

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            layout.label(text="Infos")
            if self.inputs[0].input_value is not None and self.inputs[0].input_value != "" and self.inputs[
                0].input_value in Data.uuid_data_storage and \
                    Data.uuid_data_storage[self.inputs[0].input_value] is not None:
                for output in (self.outputs[0], self.outputs[1], self.outputs[2], self.outputs[3]):
                    if output.name == "Duration":
                        layout.label(text=output.name + ": " + str(round(output.input_value, 4)))
                    else:
                        layout.label(text=output.name + ": " + str(output.input_value))

    def refresh_outputs(self):
        print("refresh outputs")
        if self.inputs[0].input_value != "":
            sound_sample = Data.uuid_data_storage[self.inputs[0].input_value]
            self.outputs[0].input_value = sound_sample.length
            sample_rate, channels = sound_sample.specs
            self.outputs[2].input_value = int(sample_rate)
            self.outputs[3].input_value = channels
            if sound_sample.length == -1:
                self.outputs[0].input_value = -1
            else:
                if sample_rate != 0:
                    self.outputs[1].input_value = sound_sample.length / sample_rate
                else:
                    self.outputs[1].input_value = 0
                np_array = sound_sample.data()
                length2 = len(np_array)
                if length2 != sound_sample.length:
                    print("Not same length")
                    print(sound_sample.length)
                    print(length2)

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        print("link")
        print(link)
        if isinstance(link.from_socket, SoundSampleSocket):
            self.inputs[0].input_value = link.from_socket.input_value
            self.refresh_outputs()

    def update_obm(self):
        self.update()
        for output in (self.outputs[0], self.outputs[1], self.outputs[2], self.outputs[3]):
            for link in output.links:
                # link.to_node.update_obm(self, self.outputs[0])
                link.to_node.update_obm()

    def update(self):
        # This method is called when the node updates
        print("update Sample Info node")
        self.refresh_outputs()

    def socket_update(self, socket):
        # self.glob_prop.linked_object_name = self.inputs[0].name
        print("socket_update Sound Info Node")
