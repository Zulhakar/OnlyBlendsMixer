IS_DEBUG = True
APP_NAME = "OnlyBlends.Mixer"
APP_NAME_SHORT = "obm"
OB_TREE_TYPE = 'MixerNodeTree'
NEW_NODE_GROUP_NAME = "Mixer Nodes"
NODE_EDITOR_NAME = "Onlyblends.Mixer Node Editor"

TREE_ICON = 'SOUND'

COLOR_WHITE = (1.0, 1.0, 1.0, 1.0)
COLOR_BLACK = (0.0, 0.0, 0.0, 1.0)

COLOR_SOUND_SAMPLE_SOCKET = (0.333, 0.333, 0.333, 1.0)
COLOR_SPEAKER_SOCKET = COLOR_WHITE

MIXER_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Mixer'
MIDI_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Midi'


class MixerSocketTypes:
    Sample = 'NodeSocketSample'
    Sound = 'NodeSocketSound'
    Speaker = 'NodeSocketSpeaker'

NOTE_NAMES_1 = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
NOTE_NAMES_2 = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")

########################################################################################################################
# don't change this
from .cnt.base.constants import *

CONSTANTS_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Constants'
INPUT_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Input'
GROUP_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Group'
REALTIME_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Realtime'
UTIL_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Util'
GEOMETRY_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Geometry'
MAKE_GROUP_OT_IDNAME = f'node.{APP_NAME_SHORT}_make_group'
