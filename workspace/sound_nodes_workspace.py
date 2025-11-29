import bpy

def create_my_workspace():
    name = "My Custom Workspace"

    # Workspace existiert bereits?
    for ws_key in bpy.data.workspaces:
       if name == ws_key:
           return bpy.types.BlendData.workspaces[name]

    # Neues Workspace erstellen
    ws = bpy.data.workspaces.new(name)

    # Einen neuen Screen hinzufügen
    screen = bpy.data.screens.new(name + "_screen")
    ws.screens.append(screen)

    # Area hinzufügen und layout verändern
    # Hinweis: Neue Screens haben zuerst eine einzige 3D-View-Area
    area = screen.areas[0]
    area.ui_type = 'VIEW_3D'

    # Beispiel: Sidebar öffnen
    for region in area.regions:
        print(region.type)
        if region.type == 'UI':
            region.flag ^= 4  # toggled visibility

    return ws

def register():
    ws = create_my_workspace()
    #bpy.context.window.workspace = ws