import bpy
from mido import MidiFile, tick2second
from ..mixer_node import ObmSoundNode


def new_object(ob_name, notes):
    start_time, duration, note, volume = zip(*notes)
    pos = list(zip(start_time, duration, note))
    me = bpy.data.meshes.new(ob_name + "Mesh")
    ob = bpy.data.objects.new(ob_name, me)
    # coords = [[0.0]* 3] * len(notes)
    me.from_pydata(pos, [], [])
    # ob.show_name = True
    me.update()

    # start_time_attr = me.attributes.new(name="start_time", type="FLOAT", domain="POINT")
    # start_time_attr.data.foreach_set("value", start_time)
    # duration_attr = me.attributes.new(name="duration", type="FLOAT", domain="POINT")
    # duration_attr.data.foreach_set("value", duration)
    volume_attr = me.attributes.new(name="volume", type="FLOAT", domain="POINT")
    volume_attr.data.foreach_set("value", volume)
    # note_attr = me.attributes.new(name="note", type="FLOAT", domain="POINT")
    # note_attr.data.foreach_set("value", note)
    return ob, me


def get_notes(midi_path, track_num, start_limit, length_limit):
    # x             y           z           volume
    # start_time    duration    note        volume
    mid = MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat
    start_time = 0.0
    final_notes = []
    final_notes_obm = []
    current_notes = {}
    for msg in mid.tracks[track_num]:
        if not msg.is_meta:
            start_time += tick2second(msg.time, ticks_per_beat, 500000)
            if length_limit > 0:
                if start_time > length_limit:
                    break
            if msg.type == 'note_on':
                key = f'{msg.channel}_{msg.note}'
                if not key in current_notes:
                    current_notes[key] = [start_time, None, msg.note, msg.velocity / 128, [msg]]
                else:
                    if msg.velocity == 0:
                        current_notes[key][4].append(msg)
                        if start_limit < start_time:
                            if current_notes[key][0] < start_limit:
                                current_notes[key][0] = start_limit
                            current_notes[key][1] = start_time
                            final_notes.append(current_notes[key])
                            obm_note = current_notes[key][:4]
                            obm_note[1] = obm_note[1] - obm_note[0]
                            obm_note[2] = ((2 ** (1 / 12)) ** (obm_note[2] - 69)) * 440
                            final_notes_obm.append(obm_note)
                        del current_notes[key]
            elif msg.type == 'note_off':
                key = f'{msg.channel}_{msg.note}'
                if key in current_notes:
                    current_notes[key][4].append(msg)
                    if start_limit < start_time:
                        if current_notes[key][0] < start_limit:
                            current_notes[key][0] = start_limit
                        current_notes[key][1] = start_time
                        final_notes.append(current_notes[key])
                        obm_note = current_notes[key][:4]
                        obm_note[1] = obm_note[1] - obm_note[0]
                        obm_note[2] = ((2 ** (1 / 12)) ** (obm_note[2] - 69)) * 440
                        final_notes_obm.append(obm_note)
                    del current_notes[key]
            else:
                for key, value in current_notes.items():
                    value[4].append(msg)
    return final_notes_obm, final_notes


class MidiToTrackObjectNode(ObmSoundNode, bpy.types.Node):
    bl_label = "MIDI to Track Object"
    bl_icon = 'EXTERNAL_DRIVE'
    last_file_name: bpy.props.StringProperty(default="")

    def init(self, context):
        self.inputs.new("NodeSocketMidi", "MIDI")
        self.inputs.new("NodeSocketIntCnt", "Track ID")
        self.inputs.new("NodeSocketFloatCnt", "Start Time")
        self.inputs.new("NodeSocketFloatCnt", "End Time")
        self.outputs.new('NodeSocketObjectCnt', "Track Object")
        self.socket_update_disabled = True
        self.inputs[2].input_value = 0.0
        self.inputs[3].input_value = -1
        self.socket_update_disabled = False
        super().init(context)

    def __del_object_if_exit(self, object_name):
        if object_name in bpy.data.objects:
            obj = bpy.data.objects[object_name]
            bpy.data.objects.remove(obj, do_unlink=True)

    def get_track(self):
        if self.inputs[0].input_value and self.inputs[0].input_value != "":
            track_num = self.inputs[1].input_value
            midi_path = self.inputs[0].input_value
            notes, _ = get_notes(midi_path, track_num, self.inputs[2].input_value, self.inputs[3].input_value)
            name = f'{self.name}_{track_num}'
            self.__del_object_if_exit(name)
            self.__del_object_if_exit(self.last_file_name)
            self.last_file_name = name


            obj, _ = new_object(name, notes)
            bpy.context.collection.objects.link(obj)
            self.outputs[0].input_value = obj

    def socket_update(self, socket):
        if not socket.is_output:
            self.get_track()
        else:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value
