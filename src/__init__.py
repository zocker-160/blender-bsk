bl_info = {
    "name" : "BSK Armature importer / exporter",
    "author" : "zocker_160",
    "description" : "addon for importing and exporting BSK armature files",
    "blender" : (2, 90, 1),
    "version" : (0, 2),
    "location" : "File > Import",
    "warning" : "This is still WiP!",
    "category" : "Import-Export",
    "tracker_url": "https://github.com/zocker-160/blender-bsk/issues"
}

import bpy
import importlib

from . import BSKimporter
from . import BSKexporter

from bpy.props import StringProperty, BoolProperty, EnumProperty
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper, ImportHelper

importlib.reload(BSKimporter)
importlib.reload(BSKexporter)

class ImportBSK(bpy.types.Operator, ImportHelper):
    """Import an BSK Armature file"""
    bl_idname = "import_armature.bsk"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import BSK"

    # ImportHelper mixin class uses this
    filename_ext = ".bsk"

    filter_glob: StringProperty(
        default="*.bsk",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        BSKimporter.main_function_import_file(filename=self.filepath)
        return {'FINISHED'}

class ExportBSK(bpy.types.Operator, ExportHelper):
    """Export an BSK Armature file"""
    bl_idname = "export_armature.bsk"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export BSK"

    filename_ext = ".bsk"

    filter_glob: StringProperty(
        default="*.bsk",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        BSKexporter.main_function_export_file(filename=self.filepath)
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportBSK.bl_idname, text="BSK Armature (.bsk)")

def menu_func_export(self, context):
    self.layout.operator(ExportBSK.bl_idname, text="BSK Armature (.bsk)")

def register():
    bpy.utils.register_class(ImportBSK)
    bpy.utils.register_class(ExportBSK)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportBSK)
    bpy.utils.unregister_class(ExportBSK)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
