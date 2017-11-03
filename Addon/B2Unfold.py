bl_info = {
    "name": "B2Unfold3D",
    "author": "Art Team at Fantastic, Yes",
    "version": (0,2),
    "blender": (2, 78, 0),
    "location": "UV > B2Unfold3D - UV Unwrapper ",
    "description": "Blender to Unfold3D bridge for Uv Unwrapping",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UV"
}

import subprocess
import os
import bpy  
import sys

def B2Unfold_LinkFunction():
    
    path = "" + bpy.app.tempdir
    path = '/'.join(path.split('\\'))
    objName = "Tmp.obj"
    originalObj = bpy.data.objects.get(bpy.context.active_object.name)

    # ---------------------------------------- Setup Scene Object ---------------------------------------
    if not bpy.context.object.data.uv_layers:
        bpy.ops.mesh.uv_texture_add()

    # ---------------------------------------------------------------------------------------------------

    bpy.ops.export_scene.obj(filepath=path + objName, check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl", use_selection=True, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=False, use_triangles=False, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=1, path_mode='AUTO')

    cmdModel_string = "U3dLoad({File={Path='" + path + objName + "', ImportGroups=true, XYZ=true}, NormalizeUVW=true})"
    print(cmdModel_string)

    cmd1_string = "U3dIslandGroups({Mode='SetGroupsProperties', MergingPolicy=8322, GroupPaths={ 'RootGroup' }, Properties={Pack={Resolution=2000}}})\n\
    U3dSelect({PrimType='Edge', Select=true, All=true, FilterIslandVisible=true})\n\
    U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={QuasiDevelopable={Developability=0.95, IslandPolyNBMin=5, FitCones=false, Straighten=true}, PipesCutter=true, HandleCutter=true, StretchLimiter=true, SkeletonUnoverlap={SegLevel=1, FromRoot=true, Smooth=2}, SQS=0.0357143, SQP=0.5, AQS=0.000178571, AQP=0.5, Smooth={Iterations=2, Force=0.5}}})\n\
    U3dCut({PrimType='Edge'})\n\
    U3dUnfold({PrimType='Edge', MinAngle=1e-005, Mix=1, Iterations=250, PreIterations=5, StopIfOutOFDomain=false, RoomSpace=0, PinMapName='Pin', ProcessNonFlats=true, ProcessSelection=true, ProcessAllIfNoneSelected=true, ProcessJustCut=true, BorderIntersections=true, TriangleFlips=true})\n\
    U3dIslandGroups({Mode='DistributeInTilesEvenly', MergingPolicy=8322, GroupPath='RootGroup'})\n\
    U3dPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup='RootGroup', Scaling={}, Rotate={}, Translate=true, LayoutScalingMode=2})\n\
    U3dOptimize({PrimType='Edge', Iterations=500, Mix=1, AngleDistanceMix=1, RoomSpace=0, MinAngle=1e-005, BorderIntersection=true, TriangleFlips=true, ProcessSelection=true, ProcessAllIfNoneSelected=true, PinMapName='Pin'})\n\
    U3dIslandGroups({Mode='DistributeInTilesByBBox', MergingPolicy=8322})\n\
    U3dIslandGroups({Mode='DistributeInTilesEvenly', MergingPolicy=8322, UseTileLocks=true, UseIslandLocks=true})\n\
    U3dPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup='RootGroup', Scaling={Mode=0}, Rotate={Mode=0}, Translate=true, LayoutScalingMode=2})\n\
    U3dSave({File={Path='" + path + objName + "', UVWProps=true}, __UpdateUIObjFileName=true})\n\
    U3dQuit()" 


    f = open(path + "Unwrap.lua", "w") 
    f.write(cmdModel_string + cmd1_string)
    f.close()

    unfold3DPath = bpy.context.scene.B2Unfold_Settings.unfold3DPath
    subprocess.run([unfold3DPath + 'unfold3d.exe', '-cfi', path + 'Unwrap.lua'])

    imported_object = bpy.ops.import_scene.obj(filepath=path + objName)
    obj_object = bpy.context.selected_objects[0]

    for obj in bpy.context.selected_objects:
            obj.select = False

    obj_object.select = True
    originalObj.select = True
    bpy.context.scene.objects.active = obj_object
    bpy.ops.object.join_uvs()

    originalObj.select = False
    
    bpy.ops.object.delete()

# ---------------------------------------- HELPER FUNCTIONS -----------------------------------------

def set_unfold3DPath(self,value):
    print(value)
    print(bpy.path.abspath(value))
    self["unfold3DPath"] = bpy.path.abspath(value) 
def get_unfold3DPath(self):
    try:
        return self['unfold3DPath']
    except:
        return ""

# ---------------------------------------- CLASS SETTINGS -------------------------------------------

class B2Unfold_Settings(bpy.types.PropertyGroup):
    unfold3DPath = bpy.props.StringProperty \
    (
        name = "",
        description = "Set the path to the Unfold3D.exe file",
        default="",
        subtype="DIR_PATH",
        get=get_unfold3DPath,
        set=set_unfold3DPath
    )


# ---------------------------------------- USER INTEFACE --------------------------------------------

class B2Unfold(bpy.types.Operator):
    """B2Unfold3D Link"""
    bl_idname = "b2unfold.link"
    bl_label = "Link"

    def execute(self, context):
        B2Unfold_LinkFunction()
        return {'FINISHED'}

class UnfoldUV(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Unfold3D Unwrap"
    bl_context = "objectmode"
    bl_idname = "Unfold_BasePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "UnfoldUV"

    def draw(self, context):
        layout = self.layout

        sendButton = layout.row()
        sendButton.scale_y = 2.5
        sendButton.operator(B2Unfold.bl_idname, text="Send To Unfold3D!", icon='TEXTURE_DATA')

        box = layout.box()
        box.label("General Options",icon = "FILTER")
        exeTitle = box.column(True)
        exeTitle.label("Unfold3D Executable Path")
        exePath = box.column(True)
        exePath.prop(bpy.context.scene.B2Unfold_Settings, 'unfold3DPath')

def register():
    bpy.utils.register_module(__name__)
    
    # Pointer Properties
    bpy.types.Scene.B2Unfold_Settings = bpy.props.PointerProperty(type=B2Unfold_Settings)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()