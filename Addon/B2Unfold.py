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
import tempfile
from sys import platform

print(str(bpy.context.scene.B2Unfold_Settings.sharpestAngle))

def B2Unfold_LinkFunction():
    
    if platform == "darwin":
        path = "" + tempfile.gettempdir()
    elif platform == "win32":
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
    " + algorithmString + "\n\
    U3dCut({PrimType='Edge'})\n\
    U3dUnfold({PrimType='Edge', MinAngle=1e-005, Mix=1, Iterations=250, PreIterations=5, StopIfOutOFDomain=false, RoomSpace=0, PinMapName='Pin', ProcessNonFlats=true, ProcessSelection=true, ProcessAllIfNoneSelected=true, ProcessJustCut=true, BorderIntersections=true, TriangleFlips=true})\n\
    U3dIslandGroups({Mode='DistributeInTilesEvenly', MergingPolicy=8322, GroupPath='RootGroup'})\n\
    U3dPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup='RootGroup', Scaling={}, Rotate={}, Translate=true, LayoutScalingMode=2})\n\
    U3dIslandGroups({Mode='DistributeInTilesByBBox', MergingPolicy=8322})\n\
    U3dIslandGroups({Mode='DistributeInTilesEvenly', MergingPolicy=8322, UseTileLocks=true, UseIslandLocks=true})\n\
    U3dPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup='RootGroup', Scaling={Mode=0}, Rotate={Mode=0}, Translate=true, LayoutScalingMode=2})\n\
    U3dSave({File={Path='" + path + objName + "', UVWProps=true}, __UpdateUIObjFileName=true})\n" 


    f = open(path + "Unwrap.lua", "w") 
    f.write(cmdModel_string + cmd1_string)
    f.close()

    unfold3DPath = bpy.context.scene.B2Unfold_Settings.unfold3DPath
    
    if platform == "darwin":
        l=os.listdir(unfold3DPath)
        appName = (str(l).strip("[]")).strip("'")
        subprocess.run([unfold3DPath + appName, '-cfi', path + 'Unwrap.lua'])
    elif platform == "win32":
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

def jangle(self, context):
    print("update called on scene ", self.name)
    # do something based on the value of "my_prop"
    if self.my_prop:
        print("It's on")
    else:
        print("It's off")
    return None

def set_algorithm(self, context):
    global algorithmCMDStrings
    global algorithmString
    algorithmString = algorithmCMDStrings[(int(self.autoSeamAlgorithm))]
    print(algorithmString)

def set_mosaicForce(value):
    
    bpy.context.scene.B2Unfold_Settings.mosaicForce = value

# ------------------------------------------- SETTINGS -----------------------------------------------

class B2Unfold_Settings(bpy.types.PropertyGroup):
    unfold3DPath = bpy.props.StringProperty \
    (
        name = "",
        description = "Set the path to the Unfold3D Application",
        default = "",
        subtype = "DIR_PATH",
        get = get_unfold3DPath,
        set = set_unfold3DPath
    )
    optimize = bpy.props.IntProperty \
    (
        name = "Interations",
        description = "Optimize UV Coordinate for less distortion (Number of iterations for the optimize algorithm)",
        default = 1,
        min = 1,
        max = 750,
    )
    autoSeamAlgorithm = bpy.props.EnumProperty \
    (
        name = "Algorithm",
        description = "This Auto Seams dropdown contains advanced algorithms to select edges automatically of the visible island set. These edges serve as a good candidate to cut and segment the islands",
                 #(identifier, name, description, icon, number)
        items = [ ('0', "Hierarchical Pelt Algorithm", ''),
                  ('1', "Mosaic Algorithm",''),
                  ('2', "Sharpest Angles Algorithm",''),
                ],
        default = '2',
        update = set_algorithm
    )

    sharpestAngle = bpy.props.IntProperty \
    (
        name = "Sharpest Angle",
        description = "Edges that have their polygon's normals forming an angle superior to this value will be selected",
        default = 60,
        min = 1,
        max = 89,
        update = jangle
    )

    mosaicForce = bpy.props.FloatProperty \
    (
        name = "Mosaic Force",
        description = "High values will segment more so the islands will be unfolded with less distortion. Low values will segment less but the cut will generate more distortion",
        default = 0.5,
        min = 0.001,
        max = 0.999,
        update = jangle
    )

algorithmCMDStrings = \
["U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={Skeleton={}, Open=true, PipesCutter=true, HandleCutter=true}})", 
"U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={QuasiDevelopable={Developability=" + str(bpy.context.scene.B2Unfold_Settings.mosaicForce) + ", IslandPolyNBMin=5, FitCones=false, Straighten=true}, PipesCutter=true, HandleCutter=true}})", 
"U3dSelect({PrimType='Edge', Select=true, ResetBefore=true, WorkingSetPrimType='Island', ProtectMapName='Protect', FilterIslandVisible=true, Auto={SharpEdges={AngleMin=" + str(bpy.context.scene.B2Unfold_Settings.sharpestAngle) + "}, PipesCutter=true, HandleCutter=true}})"
]
algorithmString = ""

# ---------------------------------------- USER INTEFACE --------------------------------------------

class B2Unfold(bpy.types.Operator):
    """B2Unfold3D Link"""
    bl_idname = "b2unfold.link"
    bl_label = "Link"

    def execute(self, context):
        B2Unfold_LinkFunction()
        return {'FINISHED'}

class MosaicButton(bpy.types.Operator):
    bl_idname = "mosaic.value"
    bl_label = "force"
    mosaicValue = bpy.props.FloatProperty()

    def execute(self, context):
        set_mosaicForce(self.mosaicValue)
        return{'FINISHED'}

class UnfoldUVMain(bpy.types.Panel):
    """Creates Main Panel in the Object properties window"""
    bl_label = "Unfold3D Main"
    bl_context = "objectmode"
    bl_idname = "Unfold_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "UnfoldUV"

    def draw(self, context):
        layout = self.layout

        # ---------- SEND BUTTON ------------
        sendButton = layout.row()
        sendButton.scale_y = 2.5
        sendButton.operator(B2Unfold.bl_idname, text="Send To Unfold3D!", icon='TEXTURE_DATA')

        # ---------- PATH INPUT -------------
        box = layout.box()
        box.label("Unfold3D Executable Path",icon = "FILTER")
        exePath = box.column(True)
        exePath.prop(bpy.context.scene.B2Unfold_Settings, 'unfold3DPath')

        # -------- SETTINGS WINDOW ----------
        settingsBox = layout.box()
        settingsBox.label("Unfold3D Settings")
        algorithmOps = settingsBox.column(True)
        algorithmOps.prop(bpy.context.scene.B2Unfold_Settings, "autoSeamAlgorithm", icon = "EDGESEL")
        
        if(bpy.context.scene.B2Unfold_Settings.autoSeamAlgorithm == '0'):
            algorithmBox = settingsBox.box()
            

        elif(bpy.context.scene.B2Unfold_Settings.autoSeamAlgorithm == '1'):
            algorithmBox = settingsBox.box()
            forceButtons = algorithmBox.row(align=True)
            forceButtons.operator(MosaicButton.bl_idname, text="1").mosaicValue = 0.25
            forceButtons.operator(MosaicButton.bl_idname, text="2").mosaicValue = 0.5
            forceButtons.operator(MosaicButton.bl_idname, text="3").mosaicValue = 0.75
            forceButtons.operator(MosaicButton.bl_idname, text="4").mosaicValue = 0.95
            algorithmBox.prop(bpy.context.scene.B2Unfold_Settings, "mosaicForce")
            
        elif(bpy.context.scene.B2Unfold_Settings.autoSeamAlgorithm == '2'):
            algorithmBox = settingsBox.box()
            algorithmBox.prop(bpy.context.scene.B2Unfold_Settings, "sharpestAngle")
        
        iterations = settingsBox.box()
        iterations.label("Optimize")
        iterations.prop(bpy.context.scene.B2Unfold_Settings, "optimize")
            

def register():
    bpy.utils.register_module(__name__)
    
    # Pointer Properties
    bpy.types.Scene.B2Unfold_Settings = bpy.props.PointerProperty(type=B2Unfold_Settings)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()