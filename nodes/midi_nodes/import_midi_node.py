import bpy
import uuid
from ..mixer_node import ObmSoundNode
from ...base.helper import get_node_id_name
from ...base.global_data import Data
from ...config import MIDI_IMPORT_OT_ID


class ImportMidiNode(ObmSoundNode, bpy.types.Node):
    bl_label = "Import MIDI"
    import_path: bpy.props.StringProperty(update=lambda self, context: self.__update_import_path())
    node_uuid: bpy.props.StringProperty()

    bl_icon = 'EXTERNAL_DRIVE'

    def init(self, context):

        self.inputs.new("NodeSocketImportMidi", "Path")
        self.outputs.new('NodeSocketMidi', "MIDI")
        super().init(context)
        self.node_uuid = str(uuid.uuid4()).replace("-", "")
        Data.create_midi_import_panel(self, self.node_uuid)

    def free(self):
        if self.node_uuid in Data.uuid_operator_class_storage:
            bpy.utils.unregister_class(Data.uuid_operator_class_storage[self.node_uuid])

    def __update_import_path(self):
        self.inputs[0].input_value = self.import_path
        self.outputs[0].input_value = self.import_path

    def refresh_outputs(self):
        self.log("refresh_outputs")
        Data.create_midi_import_panel(self, self.node_uuid)

    def socket_update(self, socket):
        super().socket_update(socket)
        if socket.is_output:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value