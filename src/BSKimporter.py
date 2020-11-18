
import bpy
import struct

from math import radians
from bpy.types import ArrayGpencilModifier
from mathutils import Vector, Matrix, Quaternion


####
# constant vars
####

MAGIC_BSK = b'JMXVBSK 0101'

#### MAIN function
def main_function_import_file(filename: str):


    with open(filename, "rb") as bskfile:

        read_uint_buff = lambda: struct.unpack("<I", bskfile.read(4))[0]


        file_type = bskfile.read(12)

        if file_type == MAGIC_BSK:
            print("This is a valid BSK file \n")
        else:
            raise TypeError(f"This filetype ({file_type}) is not supported!")

        num_bones = read_uint_buff()
        print("Number of found bones:", num_bones)

        # set object mode only works, when there is an object in the scene, otherwise it will raise RuntimeError
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass

        # prepare armature
        bpy.ops.object.armature_add(enter_editmode=False)
        Armature = bpy.context.view_layer.objects.active

        # original files use XZY axis (Z and Y are flipped), so wee need to rotate the matrix of the armature object by -90° around X
        rotM = Matrix.Rotation(radians(-90), 4, 'X')
        Armature.matrix_world = Armature.matrix_world @ rotM
        bpy.ops.object.transform_apply()

        bpy.ops.object.mode_set(mode="EDIT")
        #bpy.ops.object.editmode_toggle()
        curr_Bone = Armature.data.edit_bones[0]
        #bpy.ops.object.editmode_toggle()

        for i in range(num_bones):
            bpy.ops.object.mode_set(mode="OBJECT")

            bone_type = bskfile.read(1)
            bone_name = bskfile.read( read_uint_buff() ).decode()

            # ignore the first iteration, since the first bone is already there
            if i > 0:
                bpy.ops.object.mode_set(mode="EDIT")

                #bpy.ops.object.editmode_toggle()
                bpy.ops.armature.bone_primitive_add(name=bone_name)
                #bpy.ops.object.editmode_toggle()

                #curr_Bone = Armature.data.edit_bones[-1]
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                curr_Bone.name = bone_name

            parent_Bone_name = bskfile.read( read_uint_buff() ).decode()

            rotX, rotY, rotZ, rotW = struct.unpack("<4f", bskfile.read(16)) # this is important!! W is last value here vs in Blender it is first value!
            rotation_quad = Quaternion( (rotW, rotX, rotY, rotZ) )

            translation = Vector( struct.unpack("<3f", bskfile.read(12)) )

            
            rotX, rotY, rotZ, rotW = struct.unpack("<4f", bskfile.read(16)) # this is important!! W is last value here vs in Blender it is first value!
            rotation_quad_abs = Quaternion( (rotW, rotX, rotY, rotZ) )

            translation_abs = Vector( struct.unpack("<3f", bskfile.read(12)) )            


            # skip unknown rotations for now
            bskfile.seek(1 * (12 + 16), 1)


            pose_Bone = Armature.pose.bones[bone_name]

            if parent_Bone_name != '':
                bpy.ops.object.mode_set(mode="EDIT")
                
                edit_Bone = Armature.data.edit_bones[bone_name]
                edit_Bone.parent = Armature.data.edit_bones[parent_Bone_name]
                
                bpy.ops.object.mode_set(mode="POSE")
                
                parent_PoseBone = Armature.pose.bones[parent_Bone_name]
                pose_Bone.matrix = parent_PoseBone.matrix
                
                bpy.ops.pose.armature_apply()

            pose_Bone.location = translation
            pose_Bone.rotation_quaternion = rotation_quad

            print(bone_name, translation_abs)
            print(bone_name, rotation_quad_abs)

            num_ChildBones = read_uint_buff()

            #print("-------")
            for _ in range(num_ChildBones):
                child_BoneName = bskfile.read( read_uint_buff() ).decode()
                #print(child_BoneName)

        # apply amrature once more, otherwise the last bone would be missing in edit mode
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.armature_apply()

    print("DONE!")

    return True
