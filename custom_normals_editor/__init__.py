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

from . import normeditor_functions, normeditor_data, normeditor_piemenu


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
		
		# settings
		box = layout.box()
		box.label(' Settings')
		if editsplit:
			box.row().label("Split Normals",icon='MESH_CUBE')
			box.row().operator('object.cust_normals_clearvertsplit',text='Switch Mode')
		else:
			box.row().label("Vertex Normals",icon='OUTLINER_OB_EMPTY')
			box.row().operator('object.cust_normals_applyvertsplit',text='Switch Mode')
		box.row().operator('object.cust_normals_reset')
		
		# generate
		box = layout.box()
		box.label(' Generate')
		box.row().prop(context.window_manager, 'vn_genselectiononly',
			text='Selected Only')
		box.row().operator('object.cust_normals_gencustom')
		box.row().operator('object.cust_normals_genbent')
		
		# edit
		box = layout.box()
		box.label(' Manual Edit')
		box.row().column().prop(context.window_manager, 'vn_dirvector', text='')
		if editsplit:
			box.row().prop(context.window_manager, 'vn_selected_face', text='Index')
		box.row().prop(context.window_manager, 'vn_editselection', text='Edit Selected')
		row = box.row()
		row.operator('object.cust_normals_manualget')
		if editsplit:
			row.operator('object.cust_normals_manualset_poly')
		else:
			row.operator('object.cust_normals_manualset_vert')
		
		
		

addon_keymaps = []

def register():
	# panel
	bpy.utils.register_class(cust_normals_panel)
	# settings
	bpy.utils.register_class(normeditor_functions.cust_normals_reset)
	bpy.utils.register_class(normeditor_functions.cust_normals_applyvertsplit)
	bpy.utils.register_class(normeditor_functions.cust_normals_clearvertsplit)
	# autogen
	bpy.utils.register_class(normeditor_functions.cust_normals_gencustom)
	bpy.utils.register_class(normeditor_functions.cust_normals_genbent)
	# manual edit
	bpy.utils.register_class(normeditor_functions.cust_normals_manualset_vert)
	bpy.utils.register_class(normeditor_functions.cust_normals_manualset_poly)
	bpy.utils.register_class(normeditor_functions.cust_normals_manualget)
	# transfer
	bpy.utils.register_class(normeditor_functions.cust_normals_transfer)
	
	# pie menus functions
	bpy.utils.register_class(normeditor_piemenu.pm_opencustnormalspie)
	bpy.utils.register_class(normeditor_piemenu.pm_opengencustnormals)
	bpy.utils.register_class(normeditor_piemenu.pm_openeditcustnormals)
	bpy.utils.register_class(normeditor_piemenu.pm_opentransfercustnormals)
	# pie menu autogen presets
	bpy.utils.register_class(normeditor_piemenu.pm_normals_genbent)
	bpy.utils.register_class(normeditor_piemenu.pm_normals_gensmooth)
	# pie menus
	bpy.utils.register_class(normeditor_piemenu.PieMenu_CustNormalsBase)
	bpy.utils.register_class(normeditor_piemenu.PieMenu_CustNormalsKey)
	
	normeditor_data.initdefaults(bpy)
	
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
	
	# panel
	bpy.utils.unregister_class(cust_normals_panel)
	# settings
	bpy.utils.unregister_class(normeditor_functions.cust_normals_reset)
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
	
	# pie menu functions
	bpy.utils.unregister_class(normeditor_piemenu.pm_opencustnormalspie)
	bpy.utils.unregister_class(normeditor_piemenu.pm_opengencustnormals)
	bpy.utils.unregister_class(normeditor_piemenu.pm_openeditcustnormals)
	bpy.utils.unregister_class(normeditor_piemenu.pm_opentransfercustnormals)
	# pie menu autogen presets
	bpy.utils.unregister_class(normeditor_piemenu.pm_normals_genbent)
	bpy.utils.unregister_class(normeditor_piemenu.pm_normals_gensmooth)
	# pie menus
	bpy.utils.unregister_class(normeditor_piemenu.PieMenu_CustNormalsBase)
	bpy.utils.unregister_class(normeditor_piemenu.PieMenu_CustNormalsKey)
	
	normeditor_data.clearvars(bpy)
	

if __name__ == '__main__':
	register()
