import bpy
from .operators import (NODE_OT_my_group_tab, NODE_OT_my_make_group, MY_OT_AddSocket, NODE_PT_Sound_Group_Sockets,
                        MY_MT_add_interface, MY_OT_RemoveSelected, SOCKET_CHOICES, CUSTOM_UL_items2,
                        )
from .sound_node_tree import SoundTree, GroupStringCollectionItem
from .menus import ConstantsMenu, DeviceMenu, SampleMenu, GatewayMenu, SpeakerMenu, SoundMenu, menu_draw, draw_add_menu
from ..constants import SOUND_TREE_TYPE
addon_keymaps = []


def register_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name="Node Editor", space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(
            NODE_OT_my_group_tab.bl_idname,
            'TAB', 'PRESS'
        )
        addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()



def register():
    bpy.utils.register_class(NODE_OT_my_group_tab)
    bpy.utils.register_class(NODE_OT_my_make_group)

    bpy.utils.register_class(MY_MT_add_interface)
    bpy.utils.register_class(MY_OT_AddSocket)
    bpy.utils.register_class(MY_OT_RemoveSelected)
    bpy.utils.register_class(NODE_PT_Sound_Group_Sockets)
    bpy.utils.register_class(CUSTOM_UL_items2)

    register_keymap()

    bpy.types.NODE_MT_add.append(draw_add_menu)

    bpy.types.NODE_MT_context_menu.append(menu_draw)
    #bpy.types.NODE_MT_node.prepend(menu_draw)


    bpy.utils.register_class(ConstantsMenu)
    bpy.utils.register_class(DeviceMenu)
    bpy.utils.register_class(SampleMenu)
    bpy.utils.register_class(GatewayMenu)
    bpy.utils.register_class(SpeakerMenu)
    bpy.utils.register_class(SoundMenu)

    bpy.utils.register_class(GroupStringCollectionItem)
    bpy.utils.register_class(SoundTree)


def unregister():
    unregister_keymap()
    bpy.utils.unregister_class(NODE_OT_my_group_tab)
    bpy.utils.unregister_class(NODE_OT_my_make_group)

    bpy.utils.unregister_class(MY_MT_add_interface)
    bpy.utils.unregister_class(MY_OT_AddSocket)
    bpy.utils.unregister_class(MY_OT_RemoveSelected)
    bpy.utils.unregister_class(NODE_PT_Sound_Group_Sockets)
    bpy.utils.unregister_class(CUSTOM_UL_items2)


    bpy.types.NODE_MT_context_menu.remove(menu_draw)
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    bpy.utils.unregister_class(ConstantsMenu)
    bpy.utils.unregister_class(DeviceMenu)
    bpy.utils.unregister_class(SampleMenu)
    bpy.utils.unregister_class(GatewayMenu)
    bpy.utils.unregister_class(SpeakerMenu)
    bpy.utils.unregister_class(SoundMenu)

    bpy.utils.unregister_class(GroupStringCollectionItem)
    bpy.utils.unregister_class(SoundTree)



