import bpy
import aud

import numpy as np
import os
from .global_data import Data
from .aud_helper import import_wave_file, wav_metadata

def import_wav(filepath):
    wav_array  = import_wave_file(filepath)
    meta_data = wav_metadata(filepath)
    duration = meta_data.nframes / meta_data.framerate
    file_name = os.path.basename(filepath)
    channel_id = 0
    for channel in wav_array:
        coord = np.expand_dims(channel, 0)
        # x = np.zeros(len(channel))
        x = np.linspace(0, 1, len(channel))
        # x = np.expand_dims(x, 0)
        # z = x.copy()
        z = np.zeros(len(channel))
        # z = np.expand_dims(z, 0)
        coord = np.vstack([x, coord, z])
        coord = coord.T
        coord = coord.tolist()
        object_name = f"{file_name}_channel_{channel_id}"
        new_pc = point_cloud(object_name, coord)
        node_group_name = file_name.split(".wav")[0] + "_pc_from_mesh_GN"
        bpy.context.collection.objects.link(new_pc)
        geometry_nodes = point_cloud_from_mesh_gn_node_group(node_group_name)
        new_pc.modifiers.new('GeometryNodes', 'NODES')
        new_pc.modifiers['GeometryNodes'].node_group = bpy.data.node_groups[node_group_name]

        new_pc.scale = (duration, 1, 1)

        channel_id += 1


def record(option="point_cloud", attr="position", axis=1, sampling_rate=44100):
    # depsgraph = bpy.context.evaluated_depsgraph_get()
    # axis: 0, 1, 2 -> x,y,z
    objects_ = bpy.context.scene.custom
    depsgraph = bpy.context.view_layer.depsgraph
    track = []
    element = bpy.data.objects[objects_[0].name]

    channel_id = objects_[0].obj_id
    print(objects_[0].obj_type)

    obj_eval = depsgraph.id_eval_get(element)
    geometry = obj_eval.evaluated_geometry()
    pc = geometry.pointcloud
    if pc is None:
        print("No Pointcloud exist, only pointcloud are playable")

    attr_data = pc.attributes[attr].data
    # t_uple = tuple(attr_data)
    length_of_data = len(attr_data)
    duration = length_of_data / sampling_rate
    for vert in attr_data:
        v = vert.vector
        # print(v)
        v_tup = tuple(v)
        track.append(v_tup[axis])
        # print(v_tup)

    Data.persistent_data.extend(track)
    bpy.context.scene.mixer_props.record_duration = len(Data.persistent_data) / sampling_rate
    arr = 32767 * np.asarray(track)

    # to do specific channels
    sound_array = np.asarray([arr, arr]).T.astype(np.int16)
    pygame.mixer.quit()
    pygame.mixer.init(channels=2)

    sound = pygame.sndarray.make_sound(sound_array.copy())

    if Data.channel is None:
        Data.channel = sound.play()
    else:
        if Data.channel.get_busy():
            Data.channel.queue(sound)
        else:
            Data.channel = sound.play()
    return duration



def play_selection(obj_, option="point_cloud", attr="position", axis=1, sampling_rate=44100):
    # depsgraph = bpy.context.evaluated_depsgraph_get()
    # axis: 0, 1, 2 -> x,y,z
    if option == "point_cloud":
        depsgraph = bpy.context.view_layer.depsgraph
        channels = []



        track = []
        obj_eval = depsgraph.id_eval_get(obj_)
        geometry = obj_eval.evaluated_geometry()
        pc = geometry.pointcloud

        attr_data = pc.attributes[attr].data
        # t_uple = tuple(attr_data)
        length_of_data = len(attr_data)
        duration = length_of_data / sampling_rate
        for vert in attr_data:
            v = vert.vector
            v_tup = tuple(v)
            track.append(v_tup[1])
        channels.append(track)

        for cha in channels:
            sound_array = np.asarray([cha]).T.astype(np.float32)
            sou = aud.Sound.buffer(sound_array, sampling_rate)
            device = aud.Device()
            h = device.play(sou)
    return duration

def play_sample(device, sound):
    handle = device.play(sound)

def stop_play(device):
    device.stopAll()

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


def point_cloud(ob_name, coords):
    """Create point cloud object based on given coordinates and name."""
    me = bpy.data.meshes.new(ob_name + "Mesh")
    ob = bpy.data.objects.new(ob_name, me)
    me.from_pydata(coords, [], [])
    # ob.show_name = True
    me.update()
    return ob
