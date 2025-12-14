import bpy
from .operators import operator_classes
from .sound_node_tree import SoundTree, GroupStringCollectionItem, GroupSocketCollectionItem
from .menus import ConstantsMenu, DeviceMenu, SampleMenu, SpeakerMenu, SoundMenu, menu_draw, draw_add_menu
from .operators import NODE_OT_my_group_tab
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

    for o_class in operator_classes:
        print(o_class)
        bpy.utils.register_class(o_class)

    register_keymap()

    bpy.types.NODE_MT_add.append(draw_add_menu)

    bpy.types.NODE_MT_context_menu.append(menu_draw)

    bpy.utils.register_class(ConstantsMenu)
    bpy.utils.register_class(DeviceMenu)
    bpy.utils.register_class(SampleMenu)
    bpy.utils.register_class(SpeakerMenu)
    bpy.utils.register_class(SoundMenu)

    bpy.utils.register_class(GroupStringCollectionItem)
    bpy.utils.register_class(GroupSocketCollectionItem)
    bpy.utils.register_class(SoundTree)


def unregister():
    unregister_keymap()
    for o_class in reversed(operator_classes):
        bpy.utils.unregister_class(o_class)

    bpy.types.NODE_MT_context_menu.remove(menu_draw)
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    bpy.utils.unregister_class(ConstantsMenu)
    bpy.utils.unregister_class(DeviceMenu)
    bpy.utils.unregister_class(SampleMenu)
    bpy.utils.unregister_class(SpeakerMenu)
    bpy.utils.unregister_class(SoundMenu)

    bpy.utils.unregister_class(GroupStringCollectionItem)
    bpy.utils.unregister_class(GroupSocketCollectionItem)
    bpy.utils.unregister_class(SoundTree)



