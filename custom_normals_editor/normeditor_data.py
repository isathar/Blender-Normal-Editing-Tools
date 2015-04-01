############################################################
# variables init + cleanup


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
		default=1.0,min=0.0,max=32.0,subtype='FACTOR',
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
