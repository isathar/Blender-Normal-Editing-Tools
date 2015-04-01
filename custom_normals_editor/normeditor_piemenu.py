#############################
# Pie Menus

import bpy


# Draw functions
class PieMenu_CustNormalsBase(bpy.types.Menu):
	bl_label = ''
	
	def execute(self, context):
		return {'FINISHED'}
	
	def draw(self, context):
		if context.mode == 'OBJECT' or context.mode == 'EDIT_MESH':
			layout = self.layout
			pie = layout.menu_pie()
			
			if context.window_manager.pmui_show_generate:
				pie.label('   Generate')
				pie.operator('object.pm_normals_gensmooth', text='Smooth', icon='MESH_CUBE')
				pie.operator('object.pm_normals_genbent', text='Bent', icon='MESH_CUBE')
				pie.operator('object.pm_opencustnormalspie', text="Back", icon='CANCEL')
				pie.operator('object.cust_normals_reset', text="Default", icon='MESH_CUBE')
			elif context.window_manager.pmui_show_edit:
				pie.label('   Edit')
				pie.operator('object.cust_normals_manualget', text="Get", icon='SCENE_DATA')
				if context.window_manager.edit_splitnormals:
					pie.operator('object.cust_normals_manualset_poly', text="Set", icon='SCENE_DATA')
				else:
					pie.operator('object.cust_normals_manualset_vert', text="Set", icon='SCENE_DATA')
				pie.operator('object.pm_opencustnormalspie', text="Back", icon='CANCEL')
			elif context.window_manager.pmui_show_transfer:
				pie.label('   Transfer')
				pie.operator('object.editnormals_transfer', text="Default", icon='CANCEL')
				pie.operator('object.cust_normals_transfer', text="Custom", icon='CANCEL')
				pie.operator('object.pm_opencustnormalspie', text="Back", icon='CANCEL')
				row = pie.box()
				row.label('Source')
				row.row().prop_search(context.window_manager, 
					"normtrans_sourceobj", 
					context.scene, 
					"objects", 
					"",
					"",
					False,
					'MESH_CUBE'
				)
			else:
				pie.label('   Normals Editor')
				pie.operator('object.pm_opengencustnormals', text="Generate", icon='SCENE_DATA')
				pie.operator('object.pm_openeditcustnormals', text="Edit", icon='SCENE_DATA')
				pie.operator('object.pm_opentransfercustnormals', text="Transfer", icon='SCENE_DATA')
				if context.window_manager.edit_splitnormals:
					pie.operator('object.cust_normals_clearvertsplit',text='Mode: Split', icon='MESH_CUBE')
				else:
					pie.operator('object.cust_normals_applyvertsplit',text='Mode: Vertex', icon='OUTLINER_OB_EMPTY')
			

# keybind function
class PieMenu_CustNormalsKey(bpy.types.Menu):
	bl_label = ''
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = False, False, False
		return {'FINISHED'}
	
	def draw(self, context):
		if context.mode == 'OBJECT' or context.mode == 'EDIT_MESH':
			layout = self.layout
			pie = layout.menu_pie()
			
			pie.label('  Normals Editor')
			pie.operator('object.pm_opengencustnormals', text="Generate", icon='SCENE_DATA')
			pie.operator('object.pm_openeditcustnormals', text="Edit", icon='SCENE_DATA')
			pie.operator('object.pm_opentransfercustnormals', text="Transfer", icon='SCENE_DATA')
			if context.window_manager.edit_splitnormals:
				pie.operator('object.cust_normals_clearvertsplit',text='Mode: Split', icon='MESH_CUBE')
			else:
				pie.operator('object.cust_normals_applyvertsplit',text='Mode: Vertex', icon='OUTLINER_OB_EMPTY')


# Pick pie menu to display:

# - Main -
class pm_opencustnormalspie(bpy.types.Operator):
	bl_idname = 'object.pm_opencustnormalspie'
	bl_label = 'Manual Edit'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = False, False, False
		bpy.ops.wm.call_menu_pie(name='PieMenu_CustNormalsBase')
		return {'FINISHED'}

# - Generate -
class pm_opengencustnormals(bpy.types.Operator):
	bl_idname = 'object.pm_opengencustnormals'
	bl_label = 'Generate'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = True, False, False
		bpy.ops.wm.call_menu_pie(name='PieMenu_CustNormalsBase')
		return {'FINISHED'}

# - Edit -
class pm_openeditcustnormals(bpy.types.Operator):
	bl_idname = 'object.pm_openeditcustnormals'
	bl_label = 'Edit'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = False, True, False
		bpy.ops.wm.call_menu_pie(name='PieMenu_CustNormalsBase')
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_dirvector', text='Custom Normal')

# - Transfer -
class pm_opentransfercustnormals(bpy.types.Operator):
	bl_idname = 'object.pm_opentransfercustnormals'
	bl_label = 'Transfer'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = False, False, True
		bpy.ops.wm.call_menu_pie(name='PieMenu_CustNormalsBase')
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.row().prop_search(context.window_manager, 
			"normtrans_sourceobj", 
			context.scene, 
			"objects", 
			"Source",
			"Source",
			False,
			'MESH_CUBE'
		)

# generation method buttons

# - Smooth -
class pm_normals_gensmooth(bpy.types.Operator):
	bl_idname = 'object.pm_normals_gensmooth'
	bl_label = 'Smooth'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = False, False, False	
		bpy.ops.object.cust_normals_gencustom('EXEC_DEFAULT')
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_genselectiononly', text='Selected Only')
	

# - Bent -
class pm_normals_genbent(bpy.types.Operator):
	bl_idname = 'object.pm_normals_genbent'
	bl_label = 'Bent'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		(
			context.window_manager.pmui_show_generate,
			context.window_manager.pmui_show_edit,
			context.window_manager.pmui_show_transfer
		) = False, False, False
		bpy.ops.object.cust_normals_genbent('EXEC_DEFAULT')
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_genselectiononly', text='Selected Only')

