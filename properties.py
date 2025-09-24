import bpy
from bpy.app.handlers import persistent
from .global_data import Data

def on_mesh_update(obj, scene):
    print("mesh update")
    print(obj.name)
    for node_key in Data.geometry_to_sample_nodes:
        node = Data.geometry_to_sample_nodes[node_key]
        if node.inputs[0].input_value.name == obj.name:
            print(obj.name)
            print("Operation UPDATE")
            node.operation_update()


@persistent
def on_depsgraph_update(scene):
    print("depsgraph update")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.Object):
            if update.is_updated_geometry:
                on_mesh_update(update.id, scene)

class GroupOutputCollection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Unknown")
    group_name: bpy.props.StringProperty(name="Label", default="Unknown")

class SoundSampleCollection(bpy.types.PropertyGroup):
    node_name: bpy.props.StringProperty()
    # is_played: bpy.props.BoolProperty(update=lambda self, context: self.play_function2( context))
    is_played: bpy.props.BoolProperty(default=False)
    sample_uuid: bpy.props.StringProperty()
    device_uuid: bpy.props.StringProperty()


class GatewayCollection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    socket_num: bpy.props.IntProperty()

# class GatewaySocketsCollection(bpy.types.PropertyGroup):
#     name: bpy.props.StringProperty()