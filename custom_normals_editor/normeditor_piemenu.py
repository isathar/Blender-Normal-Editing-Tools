# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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


#############################
# Pie Menus

import bpy


# Draw functions
class PieMenu_CustNormalsBase(bpy.types.Menu):
	bl_label = 'Normals Editor'
	
	def execute(self, context):
		return {'FINISHED'}
	
	def draw(self, context):
		if context.mode == 'OBJECT' or context.mode == 'EDIT_MESH':
			layout = self.layout
			pie = layout.menu_pie()
			
			if context.window_manager.pmui_show_generate:
				pie.label('   Generate')
				pie.operator('object.cust_normals_gendefault', text="Default", icon='OBJECT_DATA')
				pie.operator('object.cust_normals_genbent', text='Bent', icon='OBJECT_DATA')
				pie.operator('object.pm_opencustnormalspie', text="Back", icon='PANEL_CLOSE')
				pie.operator('object.cust_normals_gencustom', text='Smooth', icon='OBJECT_DATA')
			elif context.window_manager.pmui_show_edit:
				pie.label('   Edit')
				pie.operator('object.cust_normals_manualget', text="Get", icon='EDIT_VEC')
				if context.window_manager.edit_splitnormals:
					pie.operator('object.cust_normals_manualset_poly', text="Set", icon='EDIT_VEC')
				else:
					pie.operator('object.cust_normals_manualset_vert', text="Set", icon='EDIT_VEC')
				pie.operator('object.pm_opencustnormalspie', text="Back", icon='PANEL_CLOSE')
			elif context.window_manager.pmui_show_transfer:
				pie.label('   Transfer')
				pie.operator('object.editnormals_transfer', text="Default", icon='SCENE_DATA')
				pie.operator('object.cust_normals_transfer', text="Custom", icon='SCENE_DATA')
				pie.operator('object.pm_opencustnormalspie', text="Back", icon='PANEL_CLOSE')
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
				pie.label('   Main')
				pie.operator('object.pm_opengencustnormals', text="Generate", icon='MESH_CUBE')
				pie.operator('object.pm_openeditcustnormals', text="Edit", icon='EDIT_VEC')
				pie.operator('object.pm_opentransfercustnormals', text="Transfer", icon='SCENE_DATA')
				if context.window_manager.edit_splitnormals:
					pie.operator('object.cust_normals_clearvertsplit',text='Mode: Split', icon='OBJECT_DATA')
				else:
					pie.operator('object.cust_normals_applyvertsplit',text='Mode: Vertex', icon='OUTLINER_OB_EMPTY')
			

# keybind function
class PieMenu_CustNormalsKey(bpy.types.Menu):
	bl_label = 'Normals Editor'
	
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
			
			pie.label('  Main')
			pie.operator('object.pm_opengencustnormals', text="Generate", icon='MESH_CUBE')
			pie.operator('object.pm_openeditcustnormals', text="Edit", icon='EDIT_VEC')
			pie.operator('object.pm_opentransfercustnormals', text="Transfer", icon='SCENE_DATA')
			if context.window_manager.edit_splitnormals:
				pie.operator('object.cust_normals_clearvertsplit',text='Mode: Split', icon='OBJECT_DATA')
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


