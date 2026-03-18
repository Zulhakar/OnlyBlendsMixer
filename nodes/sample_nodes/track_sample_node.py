import bpy
from ..mixer_node import ObmSampleNode
from ...base.global_data import Data
import aud


def find_overlaps(events):
    # x             y           z           volume
    # start_time    duration    note        volume
    if not events:
        return []
    if len(events) <= 1:
        return []
    overlaps = []
    active_group = [0]  # (event, index)
    max_end = events[0][0] + events[0][1]
    g_i = 0
    final_stuff = []
    for i in range(1, len(events)):
        event = events[i]
        start = event[0]
        end = start + event[1]

        if start < max_end:
            overlaps.append((i, g_i))
            active_group.append(i)
            max_end = max(max_end, end)
        else:
            final_stuff.append([active_group, g_i, events[active_group[0]][0], max_end])
            active_group = [i]
            max_end = end
            g_i += 1
    if len(final_stuff) > 0 and g_i != final_stuff[-1][1]:
        final_stuff.append([active_group, g_i, events[active_group[0]][0], max_end])
    return final_stuff


def pitch_sample_from_frequency(target_frequency, sample, base_frequency=None):
    if base_frequency is None:
        length = sample.length
        sample_rate, ch_ = sample.specs
        base_frequency = 1 if length <= 0 else sample_rate / length

    pitch_factor = target_frequency / base_frequency
    pitched_sample = sample.pitch(pitch_factor)
    return pitched_sample


def mix_overlapping_group(group, parts, sample):
    resample_quality = 0
    sample_rate, ch_ = sample.specs
    start = group[2]
    end = group[3]
    final_sample = None
    for index in group[0]:
        part = parts[index]
        start_time, duration, frequency, volume = part
        end_time = start_time + duration
        start_time_diff = start_time - start
        # if start_time_diff > 0:
        start_sample = aud.Sound.silence(sample_rate).limit(0.0, start_time_diff)

        middle_sample = pitch_sample_from_frequency(frequency, sample)
        middle_sample = middle_sample.resample(sample_rate, resample_quality)
        length = middle_sample.length
        points_num = sample_rate * duration
        loop_count = 0 if length <= 0 else int((points_num / length))

        middle_sample = middle_sample.loop(loop_count)
        middle_sample = middle_sample.limit(0, duration)

        end_time_diff = end - end_time
        # if end_time_diff > 0:
        end_sample = aud.Sound.silence(sample_rate).limit(0.0, end_time_diff)
        s_m_e_sample = start_sample.join(middle_sample).join(end_sample)
        if final_sample is None:
            final_sample = s_m_e_sample
        else:
            final_sample = final_sample.mix(s_m_e_sample)
            # middle_sample = start_sample.join()

    return final_sample


class TrackSampleNode(ObmSampleNode):
    '''Create a Track Sample from a Sample and the Geometry Attributes of an Object.
     You can get this Geometry from a Midi Track Node or create it via Geometry Nodes.
     The Object need the attributes position and volume.
     The position-xyz values are mapped as x->start_time, y->duration and z->frequency.
    '''
    bl_label = "Track Sample"

    def init(self, context):
        self.inputs.new("NodeSocketObjectCnt", "Object")
        self.inputs.new("NodeSocketSample", "Sample")
        self.outputs.new("NodeSocketSample", "Sample")
        super().init(context)

    def get_attributes(self, domain="POINTCLOUD"):
        obj = self.inputs[0].input_value
        sample = None
        if self.inputs[1].input_value and self.inputs[1].input_value != "":
            sample = Data.uuid_data_storage[self.inputs[1].input_value]
        if obj and sample:
            depsgraph = bpy.context.evaluated_depsgraph_get()

            obj_eval = depsgraph.id_eval_get(obj)
            # self.node_tree.interface.active.hide_in_modifier = True
            # self.node_tree.interface.active.hide_in_modifier = False
            if obj_eval.is_evaluated:
                geometry = obj_eval.evaluated_geometry()
                domain_data = None
                if domain == "POINTCLOUD":
                    domain_data = geometry.pointcloud
                elif domain == "MESH":
                    domain_data = geometry.mesh
                if domain_data is None:
                    return None

                attr_list = ["position", "volume"]
                st_attr = domain_data.attributes[attr_list[0]]
                n = len(st_attr.data)
                attr_dict = {}
                for attr in attr_list:
                    attr_dict[attr] = domain_data.attributes[attr].data.values()
                sequence = []
                for i in range(0, n):
                    pack = []
                    for attr in attr_list:
                        value = attr_dict[attr][i]
                        if attr == "position":
                            #start_time , note, volume = value.value
                            pack.extend(tuple(value.vector))
                        else:
                            pack.append(value.value)
                    sequence.append(pack)

                sequence = sorted(sequence, key=lambda x: x[0])

                d = find_overlaps(sequence)
                # for item in sequence:
                #    end_time = item[0] + item[1]
                final_sample = None
                for item in d:
                    mixed_sample = mix_overlapping_group(item, sequence, sample)
                    if final_sample is None:
                        final_sample = mixed_sample
                    else:
                        final_sample = final_sample.join(mixed_sample)

                Data.uuid_data_storage[self.node_uuid] = final_sample
                self.outputs[0].input_value = self.node_uuid

        else:
            if self.outputs[0].input_value and self.outputs[0].input_value in Data.uuid_data_storage:
                del Data.uuid_data_storage[self.outputs[0].input_value]
                self.outputs[0].input_value = ""
            return None

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket != self.outputs[0]:
            if socket == self.inputs[1]:
                if self.inputs[1].input_value in Data.uuid_data_storage and Data.uuid_data_storage[self.inputs[1].input_value] :
                    Data.uuid_data_storage[self.inputs[1].input_value] = Data.uuid_data_storage[self.inputs[1].input_value].cache()
            self.get_attributes("MESH")
        else:
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value