import copy
import wave

import bpy
import aud
import numpy as np
from .constants import NOTE_NAMES_1, NOTE_NAMES_2, VERSATILE_SOCKET_SHAPE, SINGLE_VALUES_SOCKET_SHAPE, FIELDS_SOCKET_SHAPE


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

def get_socket_index(sockets, socket):
    for i , value in enumerate(sockets):
        if socket == value:
            return i
    return None

def _checker(self, tree):
    parent = self.parent_node_tree
    while parent:
        if tree == parent:
            return False
        parent = parent.parent
    return True


def create_note_dict():
    # source: https://en.wikipedia.org/wiki/Piano_key_frequencies
    octaves_num = 9
    notes_num = 12
    names_1 = NOTE_NAMES_1
    names_2 = NOTE_NAMES_2
    current_index = 0
    midi_note_index = 12
    piano_key_number_index = -8

    notes_table = {}
    for octave in range(octaves_num):
        for note_index in range(notes_num):
            current_note_name1 = names_1[note_index] + str(octave)
            current_note_name2 = names_2[note_index] + str(octave)
            frequency = ((2 ** (1 / 12)) ** (piano_key_number_index - 49)) * 440
            notes_table[current_note_name1] = (current_note_name1, current_note_name2, midi_note_index,
                                               piano_key_number_index, frequency)
            current_index += 1
            midi_note_index += 1
            piano_key_number_index += 1

    return notes_table, ("name1", "name2", "midi_note_index", "piano_key_number_index", "frequency")


def create_note_enum_items(notes_table):
    notes = []
    for key, value in notes_table.items():
        description = f"Note: {value[0]}/{value[1]}, Frequency: {value[4]} Hz, Midi Note Index: {value[2]}, Piano Key: {value[3]}"
        notes.append((value[0], value[0],
                      description))
    # sorted_notes = sorted(notes, key=lambda item: item[2])
    return notes


def wav_metadata(filename):
    with wave.open(filename) as wav_file:
        metadata = wav_file.getparams()
        return metadata


def import_wave_file(filename):
    sound = aud.Sound(filename)
    sound_np = sound.data()
    return sound_np.T


def play_wav(filename):
    device = aud.Device()

    sound = aud.Sound(filename)
    sound_array = sound.data()
    device = aud.Device()
    sound2 = aud.Sound.buffer(sound_array, 44100)
    handle2 = device.play(sound2)
    sound2.write("test.wav")


def get_length_and_specs_from_sound(sound):
    sound_aud = aud.Sound(sound.filepath)
    length = copy.deepcopy(sound_aud.length)
    specs = copy.deepcopy(sound_aud.specs)
    del sound_aud
    return length, specs  

def change_socket_shape(node):
    for socket in node.inputs:
        if socket.bl_idname != "NodeSocketVirtual":
            if bpy.app.version < (5, 0, 1):
                socket.display_shape = VERSATILE_SOCKET_SHAPE
            else:
                socket.display_shape = SINGLE_VALUES_SOCKET_SHAPE
        if socket.bl_idname == "FloatVectorFieldSocketType":
            socket.display_shape = FIELDS_SOCKET_SHAPE
    for socket in node.outputs:
        if socket.bl_idname != "NodeSocketVirtual":
            if bpy.app.version < (5, 0, 1):
                socket.display_shape = VERSATILE_SOCKET_SHAPE
            else:
                socket.display_shape = SINGLE_VALUES_SOCKET_SHAPE
        if socket.bl_idname == "FloatVectorFieldSocketType":
            socket.display_shape = FIELDS_SOCKET_SHAPE

def get_parent_node_group(in_node):
    for key, value in bpy.data.node_groups.items():
        for node in value.nodes:
            if node == in_node:
                return value
    return None

def get_obm_node_id(node):
    parent = get_parent_node_group(node)
    node_name = f"obm_{parent.name}_{node.name}"
    return node_name
