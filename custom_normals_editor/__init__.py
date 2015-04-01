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


bl_info = {
	"name": "Normals Editing Tools",
	"author": "Andreas Wiehn (isathar)",
	"version": (0, 0, 1),
	"blender": (2, 74, 0),
	"location": "View3D > Toolbar",
	"description": "Editing tools for vertex normals",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "https://github.com/isathar/Blender-Normal-Editing-Tools/issues/",
	"category": "Mesh"}


import bpy

from . import normeditor_functions, normeditor_piemenu


# UI Panel
class cust_normals_panel(bpy.types.Panel):
	bl_idname = "view3D.cust_normals_panel"
	bl_label = 'Normals Editor'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Shading / UVs"
	
	@classmethod
	def poll(self, context):
		if context.active_object != None:
			if context.active_object.type == 'MESH':
				return True
		return False
	
	def draw(self, context):
		editsplit = context.window_manager.edit_splitnormals
		layout = self.layout
		
		# mode
		box = layout.box()
		if editsplit:
			box.row().label("Split Normals",icon='OBJECT_DATA')
			box.row().operator('object.cust_normals_clearvertsplit',text='Switch Mode')
		else:
			box.row().label("Vertex Normals",icon='OUTLINER_OB_EMPTY')
			box.row().operator('object.cust_normals_applyvertsplit',text='Switch Mode')
		
		# generate
		box = layout.box()
		box.row().prop(context.window_manager, 'panelui_show_generate',
			text='Auto Generate',toggle=True)
		if context.window_manager.panelui_show_generate:
			box.row().prop(context.window_manager, 'vn_genselectiononly',
				text='Selected Only')
			box.row().operator('object.cust_normals_gendefault',text='Default')
			box.row().operator('object.cust_normals_gencustom',text='Smooth')
			box.row().operator('object.cust_normals_genbent',text='Bent')
		
		# edit
		box = layout.box()
		box.row().prop(context.window_manager, 'panelui_show_edit',
			text='Manual Edit',toggle=True)
		if context.window_manager.panelui_show_edit:
			box.row().column().prop(context.window_manager, 'vn_dirvector', text='')
			row = box.row()
			row.prop(context.window_manager, 'vn_selected_face', text='Index')
			if not editsplit:
				row.enabled = False
			box.row().prop(context.window_manager, 'vn_editselection', text='Edit Selected')
			row = box.row()
			row.operator('object.cust_normals_manualget')
			if editsplit:
				row.operator('object.cust_normals_manualset_poly')
			else:
				row.operator('object.cust_normals_manualset_vert')
		
		# transfer
		box = layout.box()
		box.row().prop(context.window_manager, 'panelui_show_transfer',
			text='Transfer',toggle=True)
		

addon_keymaps = []

def register():
	
	# settings
	bpy.utils.register_class(normeditor_functions.cust_normals_applyvertsplit)
	bpy.utils.register_class(normeditor_functions.cust_normals_clearvertsplit)
	# autogen
	bpy.utils.register_class(normeditor_functions.cust_normals_gendefault)
	bpy.utils.register_class(normeditor_functions.cust_normals_gencustom)
	bpy.utils.register_class(normeditor_functions.cust_normals_genbent)
	# manual edit
	bpy.utils.register_class(normeditor_functions.cust_normals_manualset_vert)
	bpy.utils.register_class(normeditor_functions.cust_normals_manualset_poly)
	bpy.utils.register_class(normeditor_functions.cust_normals_manualget)
	# transfer
	bpy.utils.register_class(normeditor_functions.cust_normals_transfer)
	
	# panel menu
	bpy.utils.register_class(cust_normals_panel)
	
	# pie menu functions
	bpy.utils.register_class(normeditor_piemenu.pm_opencustnormalspie)
	bpy.utils.register_class(normeditor_piemenu.pm_opengencustnormals)
	bpy.utils.register_class(normeditor_piemenu.pm_openeditcustnormals)
	bpy.utils.register_class(normeditor_piemenu.pm_opentransfercustnormals)
	# pie menu
	bpy.utils.register_class(normeditor_piemenu.PieMenu_CustNormalsBase)
	bpy.utils.register_class(normeditor_piemenu.PieMenu_CustNormalsKey)
	
	initdefaults(bpy)
	
	# add pie menu keybind
	wm = bpy.context.window_manager
	if wm.keyconfigs.addon:
		km = wm.keyconfigs.addon.keymaps.new(name='Object Non-modal')
		#kmi = km.keymap_items.new('wm.call_menu_pie', 'SLASH', 'PRESS')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'BUTTON4MOUSE', 'PRESS')
		kmi.properties.name = "PieMenu_CustNormalsKey"
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
	bpy.utils.unregister_class(normeditor_functions.cust_normals_gendefault)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_applyvertsplit)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_clearvertsplit)
	# autogen
	bpy.utils.unregister_class(normeditor_functions.cust_normals_gencustom)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_genbent)
	# manual edit
	bpy.utils.unregister_class(normeditor_functions.cust_normals_manualset_vert)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_manualset_poly)
	bpy.utils.unregister_class(normeditor_functions.cust_normals_manualget)
	# transfer
	bpy.utils.unregister_class(normeditor_functions.cust_normals_transfer)
	
	# panel menu
	bpy.utils.unregister_class(cust_normals_panel)
	
	# pie menu functions
	bpy.utils.unregister_class(normeditor_piemenu.pm_opencustnormalspie)
	bpy.utils.unregister_class(normeditor_piemenu.pm_opengencustnormals)
	bpy.utils.unregister_class(normeditor_piemenu.pm_openeditcustnormals)
	bpy.utils.unregister_class(normeditor_piemenu.pm_opentransfercustnormals)
	# pie menu
	bpy.utils.unregister_class(normeditor_piemenu.PieMenu_CustNormalsBase)
	bpy.utils.unregister_class(normeditor_piemenu.PieMenu_CustNormalsKey)
	
	clearvars(bpy)


def initdefaults(bpy):
	import sys
	
	types = bpy.types
	
	types.WindowManager.edit_splitnormals = bpy.props.BoolProperty(
		default=False)
	
	# Generate
	types.WindowManager.vn_genselectiononly = bpy.props.BoolProperty(
		default=False,
		description='Generate normals for selected vertices only')
	types.WindowManager.vn_bendingratio = bpy.props.FloatProperty(
		default=1.0,min=0.0,max=1.0,subtype='FACTOR',
		description='Ratio between current and bent normals')
	types.WindowManager.vn_falloff = bpy.props.FloatProperty(
		default=1.0,min=0.0,max=1.0,subtype='FACTOR',
		description='Distance falloff factor')
	
	# Manual Edit
	types.WindowManager.vn_dirvector = bpy.props.FloatVectorProperty(
		default=(0.0,0.0,1.0),subtype='TRANSLATION',max=1.0,min=-1.0)
	types.WindowManager.vn_editselection = bpy.props.BoolProperty(
		default=False,
		description='Edit all normals on selected face')
	types.WindowManager.vn_selected_face = bpy.props.IntProperty(
		default=0,min=-1,max=3,
		description='Index of the selected normal on the face')
	
	# Transfer
	types.WindowManager.normtrans_sourceobj = bpy.props.StringProperty(
		default='',description='Object to get normals from')
	types.WindowManager.normtrans_influence = bpy.props.FloatProperty(
		description='Transfer strength, negative inverts',
		subtype='FACTOR',min=-1.0,max=1.0,default=1.0)
	types.WindowManager.normtrans_maxdist = bpy.props.FloatProperty(
		description='Transfer distance, 0 for infinite',
		subtype='DISTANCE',unit='LENGTH',
		min=0.0,max=sys.float_info.max,soft_max=20.0,default=0.01)
	types.WindowManager.normtrans_bounds = bpy.props.EnumProperty(
		name='Boundary Edges',
		description='Management for single-face edges.',
		items=[('IGNORE', 'Ignore', 'Discard source boundary edges.'),
			   ('INCLUDE', 'Include', 'Include source boundary edges.'),
			   ('ONLY', 'Only', 'Operate only on boundary edges.')],
		default='IGNORE'
		)
	
	types.WindowManager.panelui_show_generate = bpy.props.BoolProperty(
		default=False)
	types.WindowManager.panelui_show_edit = bpy.props.BoolProperty(
		default=False)
	types.WindowManager.panelui_show_transfer = bpy.props.BoolProperty(
		default=False)
	
	types.WindowManager.pmui_show_generate = bpy.props.BoolProperty(
		default=False)
	types.WindowManager.pmui_show_edit = bpy.props.BoolProperty(
		default=False)
	types.WindowManager.pmui_show_transfer = bpy.props.BoolProperty(
		default=False)
	
	del types, sys


def clearvars(bpy):
	props = ['edit_splitnormals',
	'vn_genselectiononly','vn_bendingratio',
	'vn_dirvector',
	'vn_editselection','vn_selected_face',
	'normtrans_sourceobj','normtrans_influence',
	'normtrans_maxdist','normtrans_bounds']
	
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
