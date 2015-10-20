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

################################################
# 		Notes/Attributions:
#
# normeditor_functions.cust_normals_transfer_tovert:
# - concept based on Vrav's Transfer Vertex Normals
# - http://blenderartists.org/forum/showthread.php?259554-Addon-EditNormals-Transfer-Vertex-Normals
#
# normeditor_functions.cust_normals_genweighted_area:
# - concept based on http://www.bytehazard.com/articles/vertnorm.html 
#   - (Martin Buijs, 2007)


bl_info = {
	"name": "Normals Editing Tools",
	"author": "Andreas Wiehn (isathar)",
	"version": (1, 0, 3),
	"blender": (2, 74, 0),
	"location": "View3D > Toolbar",
	"description": "Editing tools for vertex and split vertex normals",
	"warning": "",
	"wiki_url": "https://github.com/isathar/Blender-Normal-Editing-Tools/wiki",
	"tracker_url": "https://github.com/isathar/Blender-Normal-Editing-Tools/issues/",
	"category": "Mesh"}


import bpy

from . import normeditor_functions


# UI Panel
class cust_normals_panel(bpy.types.Panel):
	bl_idname = "view3D.cust_normals_panel"
	bl_label = 'Normals Editor'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Shading / UVs"
	
	@classmethod
	def poll(self, context):
		return context.active_object != None
		#	if context.active_object.type == 'MESH':
		return True
		#return False
	
	def draw(self, context):
		editsplit = False
		if context.active_object != None and context.active_object.type == 'MESH':
			editsplit = context.active_object.data.use_auto_smooth
		
		layout = self.layout
		
		# mode
		box = layout.box()
		if editsplit:
			box.row().label("Split Normals",icon='OBJECT_DATA')
			box.row().operator('object.cust_normals_clearvertsplit',text='Switch Mode')
		else:
			box.row().label("Vertex Normals",icon='OUTLINER_OB_EMPTY')
			box.row().operator('object.cust_normals_applyvertsplit',text='Switch Mode')
		
		box2 = box.box()
		box2.row().label("Selection:")
		box2.row().prop(context.window_manager, 'vn_editselection',text='Selected Only')
		if context.window_manager.vn_editselection:
			box2.row().prop(context.window_manager, 'vn_editbyface',text='Face Selection')
		
		# generate
		box = layout.box()
		box.row().prop(context.window_manager, 'panelui_show_generate',
			text='Auto Generate',toggle=True)
		if context.window_manager.panelui_show_generate:
			box2 = box.box()
			box2.row().label("Mode:")
			box2.row().prop(context.window_manager, 'vn_normalsgenmode',text='')
			box2.row().prop(context.window_manager, 'vn_bendingratio',text='Ratio')
			if context.window_manager.vn_normalsgenmode == 'TRANS':
				box2.row().prop(context.window_manager, 'normtrans_maxdist',text='Distance')
			
			box2.row().operator('object.cust_normals_generate',text='Generate')
		
		# edit
		box = layout.box()
		box.row().prop(context.window_manager, 'panelui_show_edit',
			text='Edit',toggle=True)
		if context.window_manager.panelui_show_edit:
			box2 = box.box()
			if context.window_manager.vn_editmode_enabled:
				box2.row().operator('object.cust_normals_disableediting',icon='RESTRICT_VIEW_OFF')
				box2.row().prop(context.window_manager, 'vn_editmode_arrowsize', text='Arrow Scale')
			else:
				box2.row().operator('object.cust_normals_enableediting',icon='RESTRICT_VIEW_ON')
			
			box2.row().column().prop(context.window_manager, 'vn_dirvector', text='')
			
			row = box2.row()
			row.operator('object.cust_normals_manualset')
			row.operator('object.cust_normals_manualget')
			
			box2.row().operator('object.cust_normals_flipdir',text='Flip Direction')
			
		


class PieMenu_CustNormalsBase(bpy.types.Menu):
	bl_label = 'Generate'
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT' or context.mode == 'EDIT_MESH':
			if context.active_object:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		context.active_object.data.update()
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		usesplit = context.active_object.data.use_auto_smooth
		
		if usesplit:
			pie.label("Split Normals",icon='OBJECT_DATA')
		else:
			pie.label("Vertex Normals",icon='OUTLINER_OB_EMPTY')
		
		pie.operator('object.cust_normals_gencustom', text='Smooth', icon='MATCUBE')
		pie.operator('object.cust_normals_genbent', text='Bent', icon='MATSPHERE')
		pie.operator('object.cust_normals_gendefault', text="Default", icon='FILE_REFRESH')
		
		if usesplit:
			pie.operator('object.cust_normals_transfer_topoly', text="Transfer", icon='ORTHO')
			pie.operator('object.cust_normals_clearvertsplit', text="Switch Mode", icon='OBJECT_DATA')
		else:
			pie.operator('object.cust_normals_transfer_tovert', text="Transfer", icon='ORTHO')
			pie.operator('object.cust_normals_applyvertsplit', text="Switch Mode", icon='OUTLINER_OB_EMPTY')
		
		pie.operator('object.cust_normals_flipdir', text='Flip', icon='MATSPHERE')
		pie.operator('object.cust_normals_genweighted_area', text='Weighted', icon='MATCUBE')
		
		pie.operator('object.cust_normals_genflat', text='Flat', icon='EDITMODE_HLT')
		
		
		


# store keybind for cleanup
addon_keymaps = []

def register():
	# settings
	bpy.utils.register_class(normeditor_functions.cust_normals_applyvertsplit)
	bpy.utils.register_class(normeditor_functions.cust_normals_clearvertsplit)
	# autogen
	bpy.utils.register_class(normeditor_functions.cust_normals_gendefault)
	bpy.utils.register_class(normeditor_functions.cust_normals_gencustom)
	bpy.utils.register_class(normeditor_functions.cust_normals_genweighted_area)
	bpy.utils.register_class(normeditor_functions.cust_normals_genbent)
	bpy.utils.register_class(normeditor_functions.cust_normals_genflat)
	bpy.utils.register_class(normeditor_functions.cust_normals_flipdir)
	bpy.utils.register_class(normeditor_functions.cust_normals_generate)
	
	# manual edit
	bpy.utils.register_class(normeditor_functions.cust_normals_enableediting)
	bpy.utils.register_class(normeditor_functions.cust_normals_disableediting)
	bpy.utils.register_class(normeditor_functions.cust_normals_manualset)
	bpy.utils.register_class(normeditor_functions.cust_normals_manualget)
	
	# transfer
	bpy.utils.register_class(normeditor_functions.cust_normals_transfer_tovert)
	bpy.utils.register_class(normeditor_functions.cust_normals_transfer_topoly)
	
	# panel menu
	bpy.utils.register_class(cust_normals_panel)
	
	# pie menu
	bpy.utils.register_class(PieMenu_CustNormalsBase)
	
	initdefaults(bpy)
	
	# add pie menu keybind
	wm = bpy.context.window_manager
	if wm.keyconfigs.addon:
		km = wm.keyconfigs.addon.keymaps.new(name='Object Non-modal')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'BUTTON4MOUSE', 'PRESS')
		kmi.properties.name = "PieMenu_CustNormalsBase"
		addon_keymaps.append(km)


def unregister():
	# remove pie menu keybind
	wm = bpy.context.window_manager
	if wm.keyconfigs.addon:
		for km in addon_keymaps:
			for kmi in km.keymap_items:
				km.keymap_items.remove(kmi)
			wm.keyconfigs.addon.keymaps.remove(km)
	addon_keymaps.clear()
	
	# settings
	bpy.utils.unregister_class(normeditor_functions.cust_normals_applyvertsplit)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_clearvertsplit)
	# autogen
	bpy.utils.unregister_class(normeditor_functions.cust_normals_gendefault)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_gencustom)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_genweighted_area)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_genbent)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_genflat)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_flipdir)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_generate)
	# manual edit
	bpy.utils.unregister_class(normeditor_functions.cust_normals_enableediting)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_disableediting)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_manualset)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_manualget)
	
	# transfer
	bpy.utils.unregister_class(normeditor_functions.cust_normals_transfer_tovert)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_transfer_topoly)
	
	# panel menu
	bpy.utils.unregister_class(cust_normals_panel)
	
	# pie menu
	bpy.utils.unregister_class(PieMenu_CustNormalsBase)
	
	clearvars(bpy)


def initdefaults(bpy):
	types = bpy.types
	
	types.WindowManager.vn_editbyface = bpy.props.BoolProperty(
		default=False,
		description='Use selected faces instead of vertices')
	
	# Generate
	types.WindowManager.vn_bendingratio = bpy.props.FloatProperty(
		default=1.0,min=0.0,max=1.0,subtype='FACTOR',
		description='Ratio between current and generated normals')
	types.WindowManager.normtrans_maxdist = bpy.props.FloatProperty(
		description='Transfer distance, 0 for infinite',
		subtype='DISTANCE',unit='LENGTH',
		min=0.0,max=4096.0,soft_max=100.0,default=0.01)
	
	types.WindowManager.vn_normalsgenmode = bpy.props.EnumProperty(
			name="Generate Mode",
			items=(('DEFAULT', "Default", "Blender default"),
					('SMOOTH', "Smooth", "Averaged normals"),
					('WEIGHT', " Weighted ", "Averaged normals weighted by face area"),
					('BENT', " Bent ", "Bent from cursor location"),
					('FLAT', " Flat ", "*Split normals only* Set normals to face normals"),
					('TRANS', " Transfer ", "Transfer normals between objects")
					),
			default='DEFAULT'
			)
	
	# Manual Edit
	types.WindowManager.vn_dirvector = bpy.props.FloatVectorProperty(
		default=(0.0,0.0,1.0),subtype='TRANSLATION',max=1.0,min=-1.0)
	types.WindowManager.vn_editselection = bpy.props.BoolProperty(
		default=False,
		description='Edit all selected normals')

	types.WindowManager.vn_editmode_enabled = bpy.props.BoolProperty(
		default=False,
		description='Enable editing with manipulator object')
	types.WindowManager.vn_editmode_arrowsize = bpy.props.FloatProperty(
		description='Draw size scale of the manipulator arrow',
		subtype='DISTANCE',unit='LENGTH',
		min=0.1,max=16.0,soft_max=16.0,default=0.25)
	
	# ui panel vars
	types.WindowManager.panelui_show_generate = bpy.props.BoolProperty(
		default=False)
	types.WindowManager.panelui_show_edit = bpy.props.BoolProperty(
		default=False)
	types.WindowManager.panelui_show_transfer = bpy.props.BoolProperty(
		default=False)
	
	del types


def clearvars(bpy):
	props = ['vn_bendingratio',
		'vn_dirvector','vn_editselection','vn_editbyface','vn_normalsgenmode',
		'normtrans_maxdist','vn_editmode_enabled',
		'panelui_show_generate','panelui_show_edit','panelui_show_transfer'
	]
	
	for p in props:
		if bpy.context.window_manager.get(p) != None:
			del bpy.context.window_manager[p]
		try:
			x = getattr(bpy.types.WindowManager, p)
			del x
		except:
			pass
	del props[:]



if __name__ == '__main__':
	register()
