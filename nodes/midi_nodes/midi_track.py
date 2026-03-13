import bpy
from mido import MidiFile, tick2second
from ..mixer_node import ObmSoundNode


def new_object(ob_name, notes):
    me = bpy.data.meshes.new(ob_name + "Mesh")
    ob = bpy.data.objects.new(ob_name, me)
    coords = [[0.0]* 3] * len(notes)
    me.from_pydata(coords, [], [])
    # ob.show_name = True
    me.update()
    start_time, duration, volume, note = zip(*notes)
    start_time_attr = me.attributes.new(name="start_time", type="FLOAT", domain="POINT")
    start_time_attr.data.foreach_set("value", start_time)
    duration_attr = me.attributes.new(name="duration", type="FLOAT", domain="POINT")
    duration_attr.data.foreach_set("value", duration)
    volume_attr = me.attributes.new(name="volume", type="FLOAT", domain="POINT")
    volume_attr.data.foreach_set("value", volume)
    note_attr = me.attributes.new(name="note", type="FLOAT", domain="POINT")
    note_attr.data.foreach_set("value", note)
    return ob, me

def get_notes(midi_path, track_num):
    # ["start_time", "duration", "volume", "note"]
    mid = MidiFile(midi_path)
    ticks_per_beat = mid.ticks_per_beat
    current_time = 0.0
    final_notes = []
    final_notes_obm = []
    current_notes = {}
    for msg in mid.tracks[track_num]:
        if not msg.is_meta:
            current_time += tick2second(msg.time, ticks_per_beat, 500000)
            if msg.type == 'note_on':
                key = f'{msg.channel}_{msg.note}'
                if not key in current_notes:
                    current_notes[key] = [current_time, None, msg.velocity / 128, msg.note, [msg]]
                else:
                    if msg.velocity == 0:
                        current_notes[key][4].append(msg)
                        current_notes[key][1] = current_time
                        final_notes.append(current_notes[key])
                        obm_note = current_notes[key][:4]
                        obm_note[1] = obm_note[1] - obm_note[0]
                        obm_note[3] = ((2 ** (1 / 12)) ** (obm_note[3] - 69)) * 440
                        final_notes_obm.append(obm_note)
                        del current_notes[key]
            elif msg.type == 'note_off':
                key = f'{msg.channel}_{msg.note}'
                if key in current_notes:
                    current_notes[key][4].append(msg)
                    current_notes[key][1] = current_time
                    final_notes.append(current_notes[key])
                    obm_note = current_notes[key][:4]
                    obm_note[1] = obm_note[1] - obm_note[0]
                    obm_note[3] = ((2 ** (1 / 12)) ** (obm_note[3] - 69)) * 440
                    final_notes_obm.append(obm_note)
                    del current_notes[key]
            else:
                for key, value in current_notes.items():
                    value[4].append(msg)
    return final_notes_obm, final_notes


class MidiTrackNode(ObmSoundNode, bpy.types.Node):
    bl_label = "MIDI Track"
    bl_icon = 'EXTERNAL_DRIVE'

    def init(self, context):
        self.inputs.new("NodeSocketMidi", "MIDI")
        self.inputs.new("NodeSocketIntCnt", "Track Number")
        self.outputs.new('NodeSocketObjectCnt', "Object Track")
        super().init(context)

    def get_track(self):
        if self.inputs[0].input_value and self.inputs[0].input_value != "":
            track_num = self.inputs[1].input_value
            midi_path = self.inputs[0].input_value
            notes, _ = get_notes(midi_path, track_num)
            name = f'{self.name}_Track_{track_num}'
            obj, _ = new_object(name, notes)
            bpy.context.collection.objects.link(obj)
            self.outputs[0].input_value = obj

    def socket_update(self, socket):
        if not socket.is_output:
            self.get_track()
        else:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value