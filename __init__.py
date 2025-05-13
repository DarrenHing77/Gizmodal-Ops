# ##### BEGIN GPL LICENSE BLOCK #####
#
#  <An addon to blend Gizmo and Modal operations more seamlessly>
#    Copyright (C) <2022>  <Mat Brady>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.types import KeyMapItem
from bpy.app.handlers import persistent

from . import (
    operators,
    panels,
    prefs
)

bl_info = {
    "name": "Gizmodal Ops",
    "author": "Mat Brady, Blender Defender",
    "version": (1, 0, 3),
    "blender": (2, 83, 0),
    "location": "Sidebar > View Tab",
    "description": "An add-on that seamlessly blends Gizmo and Modal operations.",
    "warning": "",
    "doc_url": "https://github.com/BlenderDefender/Gizmodal-Ops#gizmodal-ops",
    "tracker_url": "https://github.com/BlenderDefender/Gizmodal-Ops/issues",
    "endpoint_url": "https://raw.githubusercontent.com/BlenderDefender/BlenderDefender/updater_endpoints/GIZMODALOPS.json",
    "category": "3D View"
}

modules = (
    operators,
    panels,
    prefs
)


@persistent
def delayed_register_keymap(dummy=None):
    print("Gizmodal Ops: Running delayed keymap registration")
    register_keymap()


def register_keymap(*args):
    print("Gizmodal Ops: Bruteforce keymap scan")
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user or wm.keyconfigs.default
    success_count = 0

    for km in kc.keymaps:
        for idname, operator in operators.keymap:
            matches = [kmi for kmi in km.keymap_items if kmi.idname == idname]
            if not matches:
                continue
            for kmi in matches:
                print(f"Rewriting {kmi.idname} to {operator.bl_idname} in keymap: {km.name}")
                kmi.idname = operator.bl_idname
                success_count += 1

    print(f"Gizmodal Ops: Bruteforce rewrite completed. {success_count} ops replaced.")


def unregister_keymap(*args):
    print("Gizmodal Ops: Bruteforce keymap restore")
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user or wm.keyconfigs.default
    restore_count = 0

    for km in kc.keymaps:
        for idname, operator in operators.keymap:
            matches = [kmi for kmi in km.keymap_items if kmi.idname == operator.bl_idname]
            if not matches:
                continue
            for kmi in matches:
                print(f"Restoring {kmi.idname} to {idname} in keymap: {km.name}")
                kmi.idname = idname
                restore_count += 1

    print(f"Gizmodal Ops: Bruteforce restore completed. {restore_count} ops restored.")



# Optional dev reload op
class DH_OT_reload_gizmodal_keymap(bpy.types.Operator):
    bl_idname = "dh.reload_gizmodal_keymap"
    bl_label = "Reload Gizmodal Keymaps"
    bl_description = "Force reload keymaps manually"

    def execute(self, context):
        unregister_keymap()
        register_keymap()
        self.report({'INFO'}, "Gizmodal keymaps reloaded.")
        return {'FINISHED'}


def register():
    print("Gizmodal Ops: Beginning registration")
    for mod in modules:
        mod.register()

    try:
        register_keymap()
    except Exception as e:
        print(f"Gizmodal Ops: Immediate keymap registration failed: {e}")

    if delayed_register_keymap not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(delayed_register_keymap)

    bpy.utils.register_class(DH_OT_reload_gizmodal_keymap)

    print("Gizmodal Ops: Registration complete")


def unregister():
    print("Gizmodal Ops: Beginning unregistration")

    if delayed_register_keymap in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(delayed_register_keymap)

    unregister_keymap()

    bpy.utils.unregister_class(DH_OT_reload_gizmodal_keymap)

    for mod in reversed(modules):
        mod.unregister()

    print("Gizmodal Ops: Unregistration complete")
