from os import write
import bpy
import struct

from math import radians
from mathutils import Matrix, Vector, Quaternion

####
# constant vars
####

MAGIC_BSK = b'JMXVBSK 0101'


def localMatrix(poseBone) -> Matrix:
    # poseBone.matrix is in object space - we need to convert it to local space 
    if poseBone.parent is not None:
        parentRefPoseMtx = poseBone.parent.bone.matrix_local
        parentPoseMtx = poseBone.parent.matrix
        
        boneRefPoseMtx = poseBone.bone.matrix_local
        bonePoseMtx = poseBone.matrix

        boneLocMtx = ( parentRefPoseMtx.inverted() @ boneRefPoseMtx ).inverted() @ ( parentPoseMtx.inverted() @ bonePoseMtx )

    else:
        boneRefPoseMtx = poseBone.bone.matrix_local
        bonePoseMtx = poseBone.matrix

        boneLocMtx = boneRefPoseMtx.inverted() @ bonePoseMtx
        
    return boneLocMtx

#### MAIN function
def main_function_export_file(filename: str):
    print("searching for armatures in the scene...")

    main_aramature = None

    # it exports the first armature it can find in the scene
    for object in bpy.data.objects:
        if object.type == 'ARMATURE':
            main_aramature = object

    if not main_aramature:
        raise ModuleNotFoundError("ERROR: no armature found!")
    else:
        print("armature found:", main_aramature.name)

    #main_aramature = bpy.data.objects['Armature']

    with open(filename, "wb") as bskfile:

        write_uint = lambda x: bskfile.write( struct.pack("<I", x) )
        
        
        bskfile.write(MAGIC_BSK)
        write_uint( len(main_aramature.pose.bones) )

        for curr_bone in main_aramature.pose.bones:
            print(curr_bone.name)

            # set bone type to primary
            bskfile.write(b'\x00')

            write_uint( len(curr_bone.name) )
            bskfile.write(curr_bone.name.encode())

            # get local matrix
            locMat = localMatrix(curr_bone)

            if curr_bone.parent:

                write_uint( len(curr_bone.parent.name) )
                bskfile.write(curr_bone.parent.name.encode())

                # calculate the transformation matrix to the origin
                transMat = curr_bone.parent.matrix.inverted() @ locMat

                # get relative transformation matrix to the parent
                relMat = curr_bone.parent.matrix.inverted() @ curr_bone.matrix

                ## relative matrix to parent
                #print("translation", relMat.to_translation())
                #print("rot_quat", relMat.to_quaternion())

                rotW, rotX, rotY, rotZ = relMat.to_quaternion()
                bskfile.write( struct.pack("<4f", rotX, rotY, rotZ, rotW) )
                bskfile.write( struct.pack("<3f", *relMat.to_translation()) )

                ## absolute Matrix to origin
                #print("abs trans", curr_bone.matrix.inverted().to_translation())
                #print("abs quat", curr_bone.matrix.inverted().to_quaternion())

                rotW, rotX, rotY, rotZ = curr_bone.matrix.inverted().to_quaternion()
                bskfile.write( struct.pack("<4f", rotX, rotY, rotZ, rotW) )
                bskfile.write( struct.pack("<3f", *curr_bone.matrix.inverted().to_translation()) )

                transMat = curr_bone.matrix.inverted() @ locMat

                ## delta Matrix
                #print("unknown trans", transMat.to_translation())
                #print("unknown rot", transMat.to_quaternion())

                rotW, rotX, rotY, rotZ = transMat.to_quaternion()
                bskfile.write( struct.pack("<4f", rotX, rotY, rotZ, rotW) )
                bskfile.write( struct.pack("<3f", *transMat.to_translation()) )
            else:
                write_uint(0)

                ## this fuck here is still not really working fucking shit

                root_matrix = curr_bone.matrix.copy()
                tMatrix = main_aramature.matrix_world @ root_matrix

                for _ in range(2):
                    rotW, rotX, rotY, rotZ = tMatrix.to_quaternion()
                    bskfile.write( struct.pack("<4f", rotX, rotY, rotZ, rotW) )
                    bskfile.write( struct.pack("<3f", *tMatrix.to_translation()) )

                transMat = curr_bone.matrix.inverted() @ locMat

                rotW, rotX, rotY, rotZ = transMat.to_quaternion()
                bskfile.write( struct.pack("<4f", rotX, rotY, rotZ, rotW) )
                bskfile.write( struct.pack("<3f", *transMat.to_translation()) )


            ## child bone crap
            write_uint(len( curr_bone.children ))

            for child in curr_bone.children:
                write_uint( len(child.name) )
                bskfile.write(child.name.encode())

        # some unknown shit at the end of the file
        bskfile.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')


    ## some old shit
    #curr_bone = main_armature.pose.bones[0]
    #curr_bone_mat = localMatrix(curr_bone)
    #loc = curr_bone_mat.inverted() @ curr_bone.head
    #loc = curr_bone.bone.matrix.inverted() @ curr_bone.head

    #print(curr_bone.name, loc)


    return True
