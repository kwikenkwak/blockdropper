import bpy
import math
import mathutils

from bpy.props import StringProperty, PointerProperty, IntProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from bpy.types import PropertyGroup, Operator

bl_info = {
    "name": "Blockdropper",
    "blender": (2, 93, 1),
    "category": "Animation",
    }

def getDirectionVector(block):
    direct = mathutils.Vector([0, 0, 0])
    directionStr = block.direction


    if directionStr == "default":
        directionStr = bpy.context.scene.dropper.defaultDirection

    if block.direction == "X+":
        direct[0] = 1
    elif block.direction == "X-":
        direct[0] = -1
    elif block.direction == "Y+":
        direct[1] = 1
    elif block.direction == "Y-":
        direct[1] = -1
    elif block.direction == "Z+":
        direct[2] = 1
    elif block.direction == "Z-":
        direct[2] = -1

    direct *= bpy.context.scene.dropper.height

    return direct
    
    
def selectedChange(self, context):
    dropper = context.scene.dropper
    if dropper.selected == -1:
        return None
    for objs in bpy.context.view_layer.objects.selected:
        objs.select_set(False)
    obj = dropper.blocks[dropper.selected].object
    context.view_layer.objects.active = obj
    obj.select_set(True)
    
def isNotUsed(objName):
    for block in bpy.context.scene.dropper.blocks:
        if block.object.name == objName:
            return False
    return True
    
def getFloorPos(obj):
    pos = obj.location.copy()
    pos[0] = math.floor(pos[0])
    pos[1] = math.floor(pos[1])
    pos[2] = math.floor(pos[2])
    
    return pos
    
def lookAndAdd(self, context, positionOffset):

    if bpy.context.view_layer.objects.active != None:
        position = bpy.context.view_layer.objects.active.location + mathutils.Vector(positionOffset)
    else:
        self.report({'WARNING'}, "No active object found")
        return 0

    position[0] = math.floor(position[0])
    position[1] = math.floor(position[1])
    position[2] = math.floor(position[2])
    
    foundPossibility = False
    
    for obj in bpy.context.view_layer.objects:
        if getFloorPos(obj) == position:
            foundPossibility = True
            if not isNotUsed(obj.name):
                continue
            dropper = bpy.context.scene.dropper
            blocks = dropper.blocks
            new = blocks.add()
            
            try:
                prev = blocks[dropper.selected]
        
                new.delay = prev.delay
                new.droptime = prev.droptime
                new.direction = prev.direction
                new.sense = prev.sense
            except IndexError:
                new.delay = -1
                new.droptime = -1
                new.direction = "default"
                new.sense = "default"
                
            new.object = obj
    
            new.name = new.object.name + ": delay=" + str(new.delay) + ", drop=" + str(new.droptime)
        
            blocks.move(len(blocks) - 1, dropper.selected + 1)
        
            dropper.selected += 1
            
            #Set this object as the selected and active object
            bpy.context.view_layer.objects.active = obj
            
            for objs in bpy.context.view_layer.objects.selected:
                objs.select_set(False)
            obj.select_set(True)
        
            return 0
        
    if foundPossibility:
        self.report({'WARNING'}, "Object is already used as a dropping block")
    else:
        self.report({'WARNING'}, "Could not find any object with that position")
        
def deleteKeyframes():
    for block in bpy.context.scene.dropper.blocks:
        try:
            obj = block.object
            
            curveRender = obj.animation_data.action.fcurves[3]
            
            keyframeframe = curveRender.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'hide_render', index = -1, frame = keyframeframe)
            
            keyframeframe = curveRender.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'hide_render', index = -1, frame = keyframeframe)
            
            curve = obj.animation_data.action.fcurves[0]
            keyframeframe = curve.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'location', index = -1, frame = keyframeframe)
            
            keyframeframe = curve.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'location', index = -1, frame = keyframeframe)

            obj.location[0] = obj.dropperLocation.x
            obj.location[1] = obj.dropperLocation.y
            obj.location[2] = obj.dropperLocation.z
            
        except (IndexError, AttributeError):
            pass
    
    
def updateName(self, context):
    dropper = context.scene.dropper
    if dropper.selected == -1:
        return None
    
    item = dropper.blocks[dropper.selected]
    
    item.name = item.object.name + ": delay=" + str(item.delay) + ", drop=" + str(item.droptime)

class BlockItem(bpy.types.PropertyGroup):
    name: StringProperty(
        name = "hoi")
    delay: IntProperty(
        name = "Delay",
        default = 10,
        update = updateName
        )
    object: PointerProperty(
        name = "Object",
        update = updateName,
        type=bpy.types.Object
        )
    droptime: IntProperty(
        name = "Droptime",
        default = 15,
        update = updateName
        )
    direction: EnumProperty(
        name = "Direction",
        description="Position the block will come from/go to",
        items=[("X-", "Left(X)","", 0), ("X+", "Right(X)", "", 1), ("Y-", "Left(Y)", "", 2),
               ("Y+", "Right(Y)", "", 3), ("Z+", "Up(Z)", "", 4), ("Z-", "Down(Z)", "", 5),
               ("default", "Default", "", 6)],
        default=4
        )
    sense: EnumProperty(
        name = "Sense",
        description="Move direction of the block",
        items=[("to", "To original location", "", 0),
               ("from", "From original location", "", 1),
               ("default", "Default", "", 2)],
        default=0
        )

class DropperObjectProperties(bpy.types.PropertyGroup):
    x: FloatProperty(
        name = "X")
    y: FloatProperty(
        name = "Y")
    z: FloatProperty(
        name = "Z")

class DropperProperties(bpy.types.PropertyGroup):
    blocks: CollectionProperty(
        name = "Blocks",
        type = BlockItem
        )
    start: IntProperty(
        name = "Starting keyframe",
        default = 0
        )
    height: IntProperty(
        name = "Dropheight",
        default = 50,
        description = "Amount of meters the blocks will be dropped from relative to their original position"
        )
    defaultDelay: IntProperty(
        name = "Default delay",
        default = 1,
        description = "Default delay that will be used for the blocks that have a delay of -1,"
        "use this mechanic to make sure you can change the delay at anytime for a lot of blocks at once"
        )
    defaultDroptime: IntProperty(
        name = "Default droptime",
        default = 30,
        description = "Default droptime that will be used for the blocks that have a droptime of -1,"
        "use this mechanic to make sure you can change the droptime at anytime for a lot of blocks at once"
        )
    defaultDirection: EnumProperty(
        name = "Direction",
        description="Position the block will come from/go to",
        items=[("X-", "Left(X)","", 0), ("X+", "Right(X)", "", 1), ("Y-", "Left(Y)", "", 2),
               ("Y+", "Right(Y)", "", 3), ("Z+", "Up(Z)", "", 4), ("Z-", "Down(Z)", "", 5)],
        default=4
        )
    defaultSense: EnumProperty(
        name = "Sense",
        description="Move direction of the block",
        items=[("to", "To original location", "", 0),
               ("from", "From original location", "", 1)],
        default=0
        )
    selected: IntProperty(
        name = "Currently selected item",
        update = selectedChange,
        default = -1
        )
    


class DropperArrayPanel(bpy.types.Panel):
    bl_idname = "DROPPERARRAY_PT_PANEL"
    bl_label = "Block array"
    bl_category = "Dropper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        
        layout = self.layout
        dropper = context.scene.dropper
        
        row = layout.row(align = True)
        row.template_list("UI_UL_list", "lines_list", dropper, "blocks", dropper, "selected", item_dyntip_propname="name")
        
        col = row.column(align = True)
        col.operator("dropper.addblock", icon = "ADD", text = "")
        col.operator("dropper.removeblock", icon = "REMOVE", text = "")
        layout.operator("dropper.findactive")
        
class DropperGeneralPanel(bpy.types.Panel):
    bl_idname = "DROPPERGENERAL_PT_PANEL"
    bl_label = "General settings"
    bl_category = "Dropper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        dropper = context.scene.dropper
        
        layout.prop(dropper, "start")
        layout.prop(dropper, "height")
        layout.prop(dropper, "defaultDelay")
        layout.prop(dropper, "defaultDroptime")
        
class DropperItemPanel(bpy.types.Panel):
    bl_idname = "DROPPERITEM_PT_PANEL"
    bl_label = "Block settings"
    bl_category = "Dropper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        dropper = context.scene.dropper
        
        try:
            currentItem = dropper.blocks[dropper.selected]
            layout.prop_search(currentItem, "object", context.scene, "objects", icon="MESH_CUBE")
            layout.prop(currentItem, "delay")
            layout.prop(currentItem, "droptime")
            layout.prop(currentItem, "direction")
            layout.prop(currentItem, "sense")
        except IndexError:
            pass
        
class DropperNavigationPanel(bpy.types.Panel):
    bl_idname = "DROPPERNAVIGATION_PT_PANEL"
    bl_label = "Block navigation"
    bl_category = "Dropper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        dropper = context.scene.dropper
        
        layout.label(text="Add neighbour")
        
        row = layout.row()
        col = row.column()
        col.alignment = 'EXPAND'
        col.label(text="X")
        col.operator("dropper.addblockxdown", text = "", icon = 'TRIA_LEFT')
        #row.label(text="X")
        col.operator("dropper.addblockxup", text = "", icon = 'TRIA_RIGHT')
        
        
        col = row.column()
        col.alignment = 'EXPAND'
        col.label(text="Y")
        col.operator("dropper.addblockyup", text = "", icon = 'TRIA_UP')
        col.operator("dropper.addblockydown", text = "", icon = 'TRIA_DOWN')
        
        
        col = row.column()
        col.alignment = 'EXPAND'
        col.label(text="Z")
        col.operator("dropper.addblockzup", text = "", icon = 'TRIA_UP')
        col.operator("dropper.addblockzdown", text = "", icon = 'TRIA_DOWN')
        
class DropperKeyframePanel(bpy.types.Panel):
    bl_idname = "DROPPERKEYFRAME_PT_PANEL"
    bl_label = "Block keyframing"
    bl_category = "Dropper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("dropper.addblockkeyframes")
        layout.operator("dropper.deletekeyframes")
        
        
        
class UpdateBlocks(bpy.types.Operator):
    bl_idname = "dropper.updateblocks"
    bl_label = "Update blocks"
    bl_description = "Update the blocks"
    
    def execute(self, context):
        return {'FINISHED'}

class AddBlockXUp(bpy.types.Operator):
    bl_idname = "dropper.addblockxup"
    bl_label = "Add block"
    bl_description = "Add the block right(X) to the currently selected one to the array"
    
    def execute(self, context):
        lookAndAdd(self, context, [1, 0, 0])
        return {'FINISHED'}
    

class AddBlockXDown(bpy.types.Operator):
    bl_idname = "dropper.addblockxdown"
    bl_label = "Add block"
    bl_description = "Add the block left(X) to the currently selected one to the array"
    
    def execute(self, context):
        lookAndAdd(self, context, [-1, 0, 0])
        return {'FINISHED'}
    

class AddBlockYUp(bpy.types.Operator):
    bl_idname = "dropper.addblockyup"
    bl_label = "Add block"
    bl_description = "Add the block above(Y) to the currently selected one to the array"
    
    def execute(self, context):
        lookAndAdd(self, context, [0, 1, 0])
        return {'FINISHED'}
 

class AddBlockYDown(bpy.types.Operator):
    bl_idname = "dropper.addblockydown"
    bl_label = "Add block"
    bl_description = "Add the block below(Y) to the currently selected one to the array"
    
    def execute(self, context):
        lookAndAdd(self, context, [0, -1, 0])
        return {'FINISHED'}
    

class AddBlockZUp(bpy.types.Operator):
    bl_idname = "dropper.addblockzup"
    bl_label = "Add block"
    bl_description = "Add the block above(Z) to the currently selected one to the array"
    
    def execute(self, context):
        lookAndAdd(self, context, [0, 0, 1])
        return {'FINISHED'}
 
class AddBlockZDown(bpy.types.Operator):
    bl_idname = "dropper.addblockzdown"
    bl_label = "Add block"
    bl_description = "Add the block below(Z) to the currently selected one to the array"
    
    def execute(self, context):
        lookAndAdd(self, context, [0, 0, -1])
        return {'FINISHED'}
    
class AddBlock(bpy.types.Operator):
    bl_idname = "dropper.addblock"
    bl_label = "Add block"
    bl_description = "Add a block"
    
    delay: IntProperty(name = "Delay")
    droptime: IntProperty(name = "Droptime")
    useActive: BoolProperty(name = "Use active object")
    object: StringProperty(name = "Object")

    direction: EnumProperty(
        name = "Direction",
        description="Position the block will come from/go to",
        items=[("X-", "Left(X)","", 0), ("X+", "Right(X)", "", 1), ("Y-", "Left(Y)", "", 2),
               ("Y+", "Right(Y)", "", 3), ("Z+", "Up(Z)", "", 4), ("Z-", "Down(Z)", "", 5),
               ("default", "Default", "", 6)],
        default=4
        )

    sense: EnumProperty(
        name = "Sense",
        description="Move direction of the block",
        items=[("to", "To original location", "", 0),
               ("from", "From original location", "", 1),
               ("default", "Default", "", 2)],
        default=0
        )

   
    def execute(self, context):
        if self.useActive:
            self.object = bpy.context.view_layer.objects.active.name
        
        if not self.object in context.scene.objects.keys():
            self.report({'WARNING'}, "Please choose a valid object")
            return {'FINISHED'}
        elif not isNotUsed(self.object):
            self.report({'WARNING'}, "Object has already been used as a block")
            return {'FINISHED'}
        

        
        dropper = context.scene.dropper
        blocks = dropper.blocks
        new = blocks.add()
        
        new.delay = self.delay
        new.object = context.scene.objects[self.object]
        new.droptime = self.droptime
        new.direction = self.direction
        new.sense = self.sense
        
        new.name = self.object + ": delay=" + str(self.delay) + ", drop=" + str(self.droptime)
        
        blocks.move(len(blocks) - 1, dropper.selected + 1)
        
        dropper.selected += 1
        
        return {'FINISHED'}

    def invoke(self, context, event):
        dropper = context.scene.dropper
        if len(dropper.blocks) != 0:
            prev = dropper.blocks[dropper.selected]
            self.delay = prev.delay
            self.droptime = prev.droptime
            self.direction = prev.direction
            self.sense = prev.sense
        else:
            self.delay = -1
            self.droptime = -1
            self.direction = "default"
            self.sense = "default"
        if bpy.context.view_layer.objects.active != None:
            self.useActive = isNotUsed(bpy.context.view_layer.objects.active.name)
        else:
            self.useActive = False
        
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "delay")
        layout.prop(self, "droptime")
        layout.prop(self, "direction")
        layout.prop(self, "sense")
        if bpy.context.view_layer.objects.active != None and isNotUsed(bpy.context.view_layer.objects.active.name):
            layout.prop(self, "useActive")
        if not self.useActive:
            layout.prop_search(self, "object", context.scene, "objects", icon="MESH_CUBE")       


class RemoveBlock(bpy.types.Operator):
    bl_idname = "dropper.removeblock"
    bl_label = "Remove block"
    bl_description = "Remove the block"
    
    def execute(self, context):
        dropper = context.scene.dropper

        if not len(dropper.blocks):
            self.report({'WARNING'}, "No item to remove")
            return {'FINISHED'}

        block = dropper.blocks[dropper.selected]
        
        try:
            obj = block.object
            
            curveRender = obj.animation_data.action.fcurves[3]
            
            keyframeframe = curveRender.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'hide_render', index = -1, frame = keyframeframe)
            
            keyframeframe = curveRender.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'hide_render', index = -1, frame = keyframeframe)
            
            curve = obj.animation_data.action.fcurves[0]
            keyframeframe = curve.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'location', index = -1, frame = keyframeframe)
            
            keyframeframe = curve.keyframe_points[0].co[0]
            obj.keyframe_delete(data_path = 'location', index = -1, frame = keyframeframe)

            obj.location[0] = obj.dropperLocation.x
            obj.location[1] = obj.dropperLocation.y
            obj.location[2] = obj.dropperLocation.z
            
        except (IndexError, AttributeError):
            pass
        
        dropper.blocks.remove(dropper.selected)

        if len(dropper.blocks) == dropper.selected:
            dropper.selected -= 1
            
        return {'FINISHED'}
    
class AddBlockKeyframes(bpy.types.Operator):
    bl_idname = "dropper.addblockkeyframes"
    bl_label = "Add keyframes"
    bl_description = "Keyframe all the blocks(and remove the possible existing ones so this is also update)"
    
    def execute(self, context):
        dropper = context.scene.dropper
        keyframed = []
        
        deleteKeyframes()
        
        frame = dropper.start
        
        for block in dropper.blocks:
            obj = block.object
            loc = obj.location

            obj.dropperLocation.x = loc[0]
            obj.dropperLocation.y = loc[1]
            obj.dropperLocation.z = loc[2]

            if obj.name in keyframed:
                deleteKeyframes()
                self.report({'WARNING'}, "Object " + obj.name + " appears multiple times in the array, this is illegal")
            keyframed.append(obj.name)
            
            droptime = block.droptime
            delay = block.delay
            
            if droptime == -1:
                droptime = dropper.defaultDroptime
                
            if delay == -1:
                delay = dropper.defaultDelay
            
            
            if block.sense == "to":
                obj.keyframe_insert(data_path = 'location', frame = frame + droptime)
            else:
                obj.keyframe_insert(data_path = 'location', frame = frame)

            obj.location += getDirectionVector(block)
            
            if block.sense == "to":
                obj.keyframe_insert(data_path = 'location', frame = frame)
            else:
                obj.keyframe_insert(data_path = 'location', frame = frame + droptime)
            

            # Keyframe visibility so that block appears/dissappears when needed

            if block.sense == "to":
                obj.hide_render = False
                obj.keyframe_insert(data_path = 'hide_render', frame = frame)
                obj.hide_render = True
                obj.keyframe_insert(data_path = 'hide_render', frame = frame - 1)
            else:
                obj.hide_render = False
                obj.keyframe_insert(data_path = 'hide_render', frame = frame + droptime)
                obj.hide_render = True
                obj.keyframe_insert(data_path = 'hide_render', frame = frame + droptime + 1)

            
            frame += delay
            
        return {'FINISHED'}
    
class DeleteKeyframes(bpy.types.Operator):
    bl_idname = "dropper.deletekeyframes"
    bl_label = "Delete keyframes"
    bl_description = "Delete all the keyframes of the objects in the array"
    
    def execute(self, context):
        deleteKeyframes()
        return {'FINISHED'}

class FindActive(bpy.types.Operator):
    bl_idname = "dropper.findactive"
    bl_label = "Find active"
    bl_description = "Search for the currently active object in the array and select the block"

    def execute(self, context):
        if bpy.context.view_layer.objects.active == None:
            self.report({'WARNING'}, "Couldn't find active object")
            return {'FINISHED'}

        dropper = context.scene.dropper
        for i in range(len(dropper.blocks)):
            if dropper.blocks[i].object == context.view_layer.objects.active:
                dropper.selected = i
                return {'FINISHED'}
        self.report({'WARNING'}, "Couldn't find active object in array")

        return {'FINISHED'}

class AutoAddBlock(bpy.types.Operator):
    bl_idname = "dropper.autoaddblock"
    bl_label = "Auto add block"
    bl_description = "Add the currently active object to the array"

    def execute(self, context):
        if bpy.context.view_layer.objects.active == None:
            self.report({'WARNING'}, "Couldn't find active object")
            return {'FINISHED'}

        obj = bpy.context.view_layer.objects.active

        if not isNotUsed(obj.name):
            self.report({'WARNING'}, "Object has already been used as a block")
            return {'FINISHED'}
        
        dropper = context.scene.dropper
        blocks = dropper.blocks
        new = blocks.add()

        if len(blocks) and dropper.selected != -1:
            prev = blocks[dropper.selected]
            new.delay = prev.delay
            new.droptime = prev.droptime
            new.direction = prev.direction
            new.sense = prev.sense
        else:
            new.delay = -1
            new.droptime = -1
            new.direction = "default"
            new.sense = "default"
            
        new.object = obj

        new.name = new.object.name + ": delay=" + str(new.delay) + ", drop=" + str(new.droptime)
        
        blocks.move(len(blocks) - 1, dropper.selected + 1)
        
        dropper.selected += 1
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AddBlockXUp)
    bpy.utils.register_class(AddBlockXDown)
    bpy.utils.register_class(AddBlockYUp)
    bpy.utils.register_class(AddBlockYDown)
    bpy.utils.register_class(AddBlockZUp)
    bpy.utils.register_class(AddBlockZDown)
    bpy.utils.register_class(AddBlock)
    bpy.utils.register_class(RemoveBlock)
    bpy.utils.register_class(UpdateBlocks)
    bpy.utils.register_class(BlockItem)

    bpy.utils.register_class(DropperProperties)
    bpy.utils.register_class(DropperObjectProperties)

    bpy.utils.register_class(FindActive)
    
    bpy.utils.register_class(DropperGeneralPanel)
    bpy.utils.register_class(DropperArrayPanel)
    bpy.utils.register_class(DropperItemPanel)
    bpy.utils.register_class(DropperNavigationPanel)
    bpy.utils.register_class(DropperKeyframePanel)
    
    bpy.utils.register_class(AddBlockKeyframes)
    bpy.utils.register_class(DeleteKeyframes)
    bpy.utils.register_class(AutoAddBlock)

    bpy.types.Scene.dropper = PointerProperty(type=DropperProperties)
    bpy.types.Object.dropperLocation = PointerProperty(type=DropperObjectProperties)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("dropper.autoaddblock", type='W', value='PRESS', ctrl=True)


def unregister():
    bpy.utils.unregister_class(AddBlockXUp)
    bpy.utils.unregister_class(AddBlockXDown)
    bpy.utils.unregister_class(AddBlockYUp)
    bpy.utils.unregister_class(AddBlockYDown)
    bpy.utils.unregister_class(AddBlockZUp)
    bpy.utils.unregister_class(AddBlockZDown)
    bpy.utils.unregister_class(AddBlock)
    bpy.utils.unregister_class(RemoveBlock)
    bpy.utils.unregister_class(UpdateBlocks)
    bpy.utils.unregister_class(BlockItem)

    bpy.utils.unregister_class(DropperProperties)
    bpy.utils.unregister_class(DropperObjectProperties)
    
    bpy.utils.unregister_class(FindActive)

    bpy.utils.unregister_class(DropperArrayPanel)
    bpy.utils.unregister_class(DropperItemPanel)
    bpy.utils.unregister_class(DropperNavigationPanel)
    bpy.utils.unregister_class(DropperGeneralPanel)
    bpy.utils.unregister_class(DropperKeyframePanel)
    
    bpy.utils.unregister_class(AddBlockKeyframes)
    bpy.utils.unregister_class(DeleteKeyframes)
    bpy.utils.unregister_class(AutoAddBlock)
if __name__ == "__main__":
    register()
