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


#	normals editor functions + classes

import bpy, bmesh, sys
from mathutils import Vector


# autogenerate + set custom normals
class cust_normals_genbent(bpy.types.Operator):
	bl_idname = 'object.cust_normals_genbent'
	bl_label = 'Generate Normals (Bent)'
	bl_description = 'Calculate normals bent towards/away from 3d cursor'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.window_manager.edit_splitnormals
		showselected = context.window_manager.vn_genselectiononly
		
		mesh = context.active_object.data
		mesh.update()
		
		bm = ''
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
		elif context.mode == 'OBJECT':
			bm = bmesh.new()
			bm.from_mesh(mesh)
		
		# build lists
		normslist = []
		selectedlist = []
		locslist = []
		
		if editsplit:
			tempverts = [v.co for v in bm.verts]
			mesh.calc_normals_split()
			loopnorms = [v.normal for v in mesh.loops]
			
			loopcount = 0
			for f in bm.faces:
				fvns = []
				for i in range(len(f.verts)):
					fvns.append(loopnorms[loopcount].copy())
					loopcount += 1
				normslist.append(fvns)
				if showselected:
					selectedlist.append(f.select)
				locslist.append([tempverts[v.index].copy() for v in f.verts])
			
			del tempverts[:]
			del loopnorms[:]
		else:
			for v in bm.verts:
				normslist.append(v.normal.copy())
				if showselected:
					selectedlist.append(v.select)
				locslist.append(v.co.copy())
		
		# calculate new normals
		cursorloc = context.scene.cursor_location
		bendratio = context.window_manager.vn_bendingratio
		
		if editsplit:
			if showselected:
				for i in range(len(normslist)):
					for j in range(len(normslist[i])):
						if selectedlist[i]:
							tempv = (locslist[i][j] - cursorloc).normalized()
							tempv = normslist[i][j] * (1.0 - bendratio) + (tempv * bendratio)
							normslist[i][j] = tempv.normalized()
			else:
				for i in range(len(normslist)):
					for j in range(len(normslist[i])):
						tempv = (locslist[i][j] - cursorloc).normalized()
						tempv = normslist[i][j] * (1.0 - bendratio) + (tempv * bendratio)
						normslist[i][j] = tempv.normalized()
		else:
			if showselected:
				for i in range(len(normslist)):
					if selectedlist[i]:
						tempv = (locslist[i] - cursorloc).normalized()
						tempv = normslist[i] * (1.0 - bendratio) + (tempv * bendratio)
						normslist[i] = tempv.normalized()
			else:
				for i in range(len(normslist)):
					tempv = (locslist[i] - cursorloc).normalized()
					tempv = normslist[i] * (1.0 - bendratio) + (tempv * bendratio)
					normslist[i] = tempv.normalized()
		
		
		# convert temp normals list to tuples
		# - should add a check for valid list here
		newnormslist = ()
		if editsplit:
			for f in normslist:
				newnormslist = newnormslist + tuple(tuple(n) for n in f)
		else:
			newnormslist = tuple(tuple(v) for v in normslist)
		
		# apply new normals to the mesh
		if editsplit:
			for e in mesh.edges:
				e.use_edge_sharp = False
			
			mesh.validate(clean_customdata=False)
			mesh.normals_split_custom_set(newnormslist)
			mesh.free_normals_split()
			mesh.update()
		else:
			if context.mode == 'EDIT_MESH':
				tverts = [v for v in bm.verts]
				for i in range(len(tverts)):
					tverts[i].normal = normslist[i].copy()
				
				bmesh.update_edit_mesh(mesh, tessface=True, destructive=True)
				mesh.update()
				
			else:
				tverts = [v for v in mesh.vertices]
				for i in range(len(tverts)):
					tverts[i].normal = normslist[i].copy()
		
		# clean up
		del normslist[:]
		del selectedlist[:]
		del locslist[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_genselectiononly', text='Selected Only')
	
	

# - Custom (weighted by number of verts)
class cust_normals_gencustom(bpy.types.Operator):
	bl_idname = 'object.cust_normals_gencustom'
	bl_label = 'Generate Normals (Smooth)'
	bl_description = 'Generate custom smooth normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.window_manager.edit_splitnormals
		showselected = context.window_manager.vn_genselectiononly
		mesh = context.active_object.data
		mesh.update()
		
		bm = ''
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
		elif context.mode == 'OBJECT':
			bm = bmesh.new()
			bm.from_mesh(mesh)
		
		# build lists
		normslist = []
		selectedlist = []
		
		if editsplit:
			tempverts = [v.co for v in bm.verts]
			mesh.calc_normals_split()
			loopnorms = [v.normal for v in mesh.loops]
			loopcount = 0
			
			for f in bm.faces:
				fvns = []
				for i in range(len(f.verts)):
					fvns.append(loopnorms[loopcount].copy())
					loopcount += 1
				normslist.append(fvns)
				if showselected:
					selectedlist.append(f.select)
			
			del tempverts[:]
			del loopnorms[:]
		else:
			for v in bm.verts:
				normslist.append(v.normal.copy())
				if showselected:
					selectedlist.append(v.select)
		
		vertslist = [v for v in bm.verts]
		bendratio = context.window_manager.vn_bendingratio
		lfindex = []
		
		# create new normals
		if editsplit:
			vindex = []
			
			for f in bm.faces:
				vindex.append([v.index for v in f.verts])
				lfindex.append([v.link_faces for v in f.verts])
			
			if showselected:
				for i in range(len(normslist)):
					if selectedlist[i]:
						for j in range(len(normslist[i])):
							fncount = 0
							tempfvect = Vector((0.0,0.0,0.0))
							for vf in lfindex[i][j]:
								if selectedlist[vf.index]:
									fncount += 1
									tempfvect = tempfvect + vf.normal
							if fncount > 0:
								tempv = (tempfvect / float(fncount)).normalized()
								tempv = (normslist[i][j] * (1.0 - bendratio)) + (tempv * bendratio)
								normslist[i][j] = tempv.normalized()
			else:
				for i in range(len(normslist)):
					for j in range(len(normslist[i])):
						fncount = len(lfindex[i][j])
						tempfvect = Vector((0.0,0.0,0.0))
						for vf in lfindex[i][j]:
							tempfvect = tempfvect + vf.normal
						if fncount > 0:
							tempv = (tempfvect / float(fncount)).normalized()
							tempv = (normslist[i][j] * (1.0 - bendratio)) + (tempv * bendratio)
							normslist[i][j] = tempv.normalized()
			
			del vindex[:]
		else:
			for v in bm.verts:
				lfindex.append(v.link_faces)
			
			if showselected:
				for i in range(len(normslist)):
					if selectedlist[i]:
						fncount = 0
						tempfvect = Vector((0.0,0.0,0.0))
						for j in range(len(lfindex[i])):
							if lfindex[i][j].select:
								fncount += 1
								tempfvect = tempfvect + lfindex[i][j].normal
						if fncount > 0:
							tempv = (tempfvect / float(fncount)).normalized()
							tempv = (normslist[i] * (1.0 - bendratio)) + (tempv * bendratio)
							normslist[i] = tempv.normalized()
			else:
				for i in range(len(normslist)):
					fncount = len(lfindex[i])
					tempfvect = Vector((0.0,0.0,0.0))
					for j in range(len(lfindex[i])):
						tempfvect = tempfvect + lfindex[i][j].normal
					if fncount > 0:
						tempv = (tempfvect / float(fncount)).normalized()
						tempv = (normslist[i] * (1.0 - bendratio)) + (tempv * bendratio)
						normslist[i] = tempv.normalized()
		
		del lfindex[:]
		del vertslist[:]
		
		# convert temp normals list to tuples
		newnormslist = ()
		if editsplit:
			for f in normslist:
				newnormslist = newnormslist + tuple(tuple(n) for n in f)
		else:
			newnormslist = tuple(tuple(v) for v in normslist)
		
		# apply new normals to the mesh
		if editsplit:
			for e in mesh.edges:
				e.use_edge_sharp = False
			mesh.validate(clean_customdata=False)
			mesh.normals_split_custom_set(newnormslist)
			mesh.free_normals_split()
			mesh.update()
		else:
			if context.mode == 'EDIT_MESH':
				tverts = [v for v in bm.verts]
				for i in range(len(tverts)):
					tverts[i].normal = normslist[i].copy()
				bmesh.update_edit_mesh(mesh, tessface=True, destructive=True)
				mesh.update()
			else:
				tverts = [v for v in mesh.vertices]
				for i in range(len(tverts)):
					tverts[i].normal = normslist[i].copy()
		
		# clean up
		del normslist[:]
		del selectedlist[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_genselectiononly', text='Selected Only')


# generate default normals
class cust_normals_gendefault(bpy.types.Operator):
	bl_idname = 'object.cust_normals_gendefault'
	bl_label = 'Generate Normals (Default)'
	bl_description = 'Generate default normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		bendratio = context.window_manager.vn_bendingratio
		
		# using split normals
		if context.window_manager.edit_splitnormals:
			tempverts = [v.select for v in mesh.vertices]
			
			mesh.calc_normals_split()
			# get old normals
			oldloopnorms = [v.normal.copy() for v in mesh.loops]
			#mesh.create_normals_split()
			# reset/generate default normals
			clearlist = tuple(tuple([0.0,0.0,0.0]) for i in range(len(mesh.vertices)))
			mesh.normals_split_custom_set_from_vertices(clearlist)
			#mesh.free_normals_split()
			
			mesh.update()
			#mesh.calc_normals_split()
			
			newloopnorms = [v.normal.copy() for v in mesh.loops]
			finalnorms = []
			
			lcount = 0
			if context.window_manager.vn_genselectiononly:
				tempverts
				for f in mesh.polygons:
					for i in range(len(f.vertices)):
						if f.select:
							tempv = (oldloopnorms[lcount] * (1.0 - bendratio)) + (newloopnorms[lcount] * bendratio)
						else:
							tempv = oldloopnorms[lcount]
						finalnorms.append(tempv)
						lcount += 1
			else:
				for i in range(len(oldloopnorms)):
					tempv = (oldloopnorms[i] * (1.0 - bendratio)) + (newloopnorms[i] * bendratio)
					finalnorms.append(tempv)
				
			
			finalnormslist = []
			loopcount = 0
			for f in mesh.polygons:
				fvns = []
				for i in range(len(f.vertices)):
					fvns.append(finalnorms[loopcount].copy())
					loopcount += 1
				finalnormslist.append(fvns)
			
			newnormslist = ()
			for f in finalnormslist:
				newnormslist = newnormslist + tuple(tuple(n) for n in f)
			
			for e in mesh.edges:
				e.use_edge_sharp = False
			mesh.validate(clean_customdata=False)
			mesh.normals_split_custom_set(newnormslist)
			mesh.free_normals_split()
			mesh.update()
			
			del newloopnorms[:]
			del oldloopnorms[:]
			del tempverts[:]
			del finalnorms[:]
			del finalnormslist[:]
			
		# using vertex normals
		else:
			bverts = [v for v in mesh.vertices]
			
			orignormals = []
			newnormals = []
			
			for v in bverts:
				orignormals.append(v.normal.copy())
			
			mesh.calc_normals()
			
			for v in bverts:
				newnormals.append(v.normal.copy())
			
			vcount = 0
			if context.window_manager.vn_genselectiononly:
				for v in bverts:
					if v.select:
						v.normal = ((orignormals[vcount] * (1.0 - bendratio)) + (newnormals[vcount] * bendratio)).normalized()
					else:
						v.normal = orignormals[vcount]
					vcount += 1
			else:
				for v in bverts:
					v.normal = ((orignormals[vcount] * (1.0 - bendratio)) + (newnormals[vcount] * bendratio)).normalized()
					vcount += 1
			
			del bverts[:]
			del orignormals[:]
			del newnormals[:]
		
		context.area.tag_redraw()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_genselectiononly', text='Selected Only')


# convert vert to split normals
class cust_normals_applyvertsplit(bpy.types.Operator):
	bl_idname = 'object.cust_normals_applyvertsplit'
	bl_label = 'Apply as Split'
	bl_description = 'Switch to split normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		
		normslist = []
		for v in mesh.vertices:
			normslist.append(v.normal.copy())
		
		newnormslist = tuple(tuple(v) for v in normslist)
		
		for e in mesh.edges:
			e.use_edge_sharp = False
		
		mesh.create_normals_split()
		mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
		mesh.validate(clean_customdata=False)
		mesh.use_auto_smooth = True
		mesh.show_edge_sharp = True
		mesh.normals_split_custom_set_from_vertices(newnormslist)
		mesh.free_normals_split()
		mesh.update()
		
		context.window_manager.edit_splitnormals = True
		
		return {'FINISHED'}

# convert split to vert normals
class cust_normals_clearvertsplit(bpy.types.Operator):
	bl_idname = 'object.cust_normals_clearvertsplit'
	bl_label = 'Clear Split Normals'
	bl_description = 'Switch to vertex normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		newnormslist = tuple(tuple((0.0,0.0,0.0)) for v in mesh.vertices)
		
		for e in mesh.edges:
			e.use_edge_sharp = False
		
		mesh.create_normals_split()
		mesh.validate(clean_customdata=False)
		mesh.use_auto_smooth = False
		mesh.show_edge_sharp = False
		mesh.normals_split_custom_set_from_vertices(newnormslist)
		mesh.free_normals_split()
		mesh.update()
		
		context.window_manager.edit_splitnormals = False
		
		bpy.ops.object.shade_smooth()
		
		return {'FINISHED'}


# Manual set/get for selection or all verts:

class cust_normals_manualset_vert(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualset_vert'
	bl_label = 'Set'
	bl_description = 'Set selected vertex normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.window_manager.edit_splitnormals:
				return context.mode == 'OBJECT'
			return context.mode == 'EDIT_MESH'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		newnorm = context.window_manager.vn_dirvector
		
		bm = bmesh.from_edit_mesh(mesh)
		vertslist = [v for v in bm.verts]
		
		if context.window_manager.vn_editselection:
			for v in vertslist:
				if v.select:
					v.normal = newnorm
		else:
			for v in vertslist:
				v.normal = newnorm
		del vertslist[:]
		
		context.area.tag_redraw()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_dirvector', text='New Normal')
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')


class cust_normals_manualset_poly(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualset_poly'
	bl_label = 'Set'
	bl_description = 'Set selected vertex normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.window_manager.edit_splitnormals:
				return context.mode == 'OBJECT'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		newnorm = context.window_manager.vn_dirvector
		
		if context.window_manager.vn_editselection:
			# need a bmesh for link_faces
			bm = ''
			if context.mode == 'EDIT_MESH':
				bm = bmesh.from_edit_mesh(mesh)
			elif context.mode == 'OBJECT':
				bm = bmesh.new()
				bm.from_mesh(mesh)
			
			selectedface = context.window_manager.vn_selected_face
			vertslist = [v for v in bm.verts]
			faceslist = [f for f in bm.faces]
			
			lfindex = []
			fcount = 0
			curface = -1
			
			for v in vertslist:
				if v.select:
					for lf in v.link_faces:
						if selectedface == -1:
							lfindex.append(lf.index)
						if fcount == selectedface:
							curface = lf.index
							lfindex.append(lf.index)
						elif lf.index == curface:
							lfindex.append(lf.index)
						fcount += 1
			
			mesh.calc_normals_split()
			
			loopnorms = [v.normal for v in mesh.loops]
			normslist = []
			
			loopcount = 0
			for f in faceslist:
				fvns = []
				for i in range(len(f.verts)):
					fvns.append(loopnorms[loopcount].copy())
					loopcount += 1
				normslist.append(fvns)
			
			for fi in lfindex:
				vcount = 0
				for v in faceslist[fi].verts:
					if vertslist[v.index].select:
						normslist[fi][vcount] = newnorm
					vcount += 1
			
			newnormslist = ()
			for f in normslist:
				newnormslist = newnormslist + tuple(tuple(n) for n in f)
			
			mesh.validate(clean_customdata=False)
			mesh.normals_split_custom_set(newnormslist)
			
			del lfindex[:]
			del vertslist[:]
			del faceslist[:]
			del normslist[:]
			del loopnorms[:]
		else:
			newnormslist = tuple(tuple((newnorm)) for v in mesh.vertices)
			
			for e in mesh.edges:
				e.use_edge_sharp = False
			
			mesh.create_normals_split()
			mesh.validate(clean_customdata=False)
			mesh.normals_split_custom_set_from_vertices(newnormslist)
		mesh.free_normals_split()
		mesh.update()
		
		context.area.tag_redraw()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_dirvector', text='New Normal')
		layout.column().prop(context.window_manager, 'vn_selected_face', text='Face Index')
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')


class cust_normals_manualget(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualget'
	bl_label = 'Get'
	bl_description = 'Get normal from selected vertex'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return context.mode == 'EDIT_MESH' or context.mode == 'OBJECT'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		mesh.update()
		if context.window_manager.edit_splitnormals:
			
			
			mesh.calc_normals_split()
			loopnorms = [v.normal.copy() for v in mesh.loops]
			mesh.free_normals_split()
			
			bm = bmesh.new()
			bm.from_mesh(mesh)
			
			mesh.update()
			normslist = []
			loopcount = 0
			
			for f in mesh.polygons:
				fvns = []
				for i in range(len(f.vertices)):
					fvns.append(loopnorms[loopcount].copy())
					loopcount += 1
				normslist.append(fvns)
			
			fcount = 0
			selectedface = context.window_manager.vn_selected_face
			if selectedface < 0:
				context.window_manager.vn_selected_face = 0
				selectedface = 0
			
			vertslist = [v for v in bm.verts]
			faceslist = [f for f in bm.faces]
			
			selfaces = []
			selverts = []
			
		
			for v in bm.verts:
				if v.select:
					for lf in v.link_faces:
						selfaces.append(lf.index)
						fvcount = 0
						for fv in lf.verts:
							if fv.select:
								selverts.append(fvcount)
								break
							fvcount += 1
					break
			
			if len(selfaces) > selectedface:
				context.window_manager.vn_dirvector = normslist[selfaces[selectedface]][selverts[selectedface]]
			
			del selfaces[:]
			del selverts[:]
		else:
			bm = ''
			if context.mode == 'EDIT_MESH':
				bm = bmesh.from_edit_mesh(mesh)
			elif context.mode == 'OBJECT':
				bm = bmesh.new()
				bm.from_mesh(mesh)
			
			vertslist = [v.normal for v in bm.verts if v.select]
			
			if len(vertslist) > 0:
				context.window_manager.vn_dirvector = vertslist[0]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		vecrow = layout.column()
		vecrow.prop(context.window_manager, 'vn_dirvector', text='Current Normal')
		vecrow.enabled = False
		layout.row().prop(context.window_manager, 'vn_selected_face', text='Face Index')


# link to transfer vertex normals with source object selection
class cust_normals_transfer(bpy.types.Operator):
	bl_idname = 'object.cust_normals_transfer'
	bl_label = 'Transfer Normals'
	bl_description = 'Transfer normals based on source object'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return context.mode == 'OBJECT'
		return False
	
	def execute(self, context):
		
		mod = sys.modules["object_transfervertexnorms"]
		if context.window_manager.normtrans_influence != 0.0:
			if context.window_manager.normtrans_bounds != 'ONLY':
				tempobjstr = context.window_manager.normtrans_sourceobj
				if tempobjstr != '':
					sourceobj = context.scene.objects[tempobjstr]
					if sourceobj != context.active_object:
						mod.transferVertexNormals(self, context, sourceobj,
								[context.active_object],
								context.window_manager.normtrans_influence,
								context.window_manager.normtrans_maxdist,
								context.window_manager.normtrans_bounds)
			else:
				mod.joinBoundaryVertexNormals(self, context, 
							[context.active_object],
							context.window_manager.normtrans_influence,
							context.window_manager.normtrans_maxdist)
		
		mesh = context.active_object.data
		
		if context.window_manager.edit_splitnormals:
			verts_list = [v.normal for v in mesh.vertices]
			newnormslist = tuple(tuple(v) for v in verts_list)
			
			for e in mesh.edges:
				e.use_edge_sharp = False
			
			mesh.create_normals_split()
			mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
			mesh.validate(clean_customdata=False)
			mesh.use_auto_smooth = True
			mesh.show_edge_sharp = True
			mesh.normals_split_custom_set_from_vertices(newnormslist)
			mesh.free_normals_split()
			mesh.update()
		
		context.area.tag_redraw()
		
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
		layout.row().prop(context.window_manager,
			'normtrans_influence', 
			text='Influence')
		layout.row().prop(context.window_manager,
			'normtrans_maxdist', 
			text='Distance')
		layout.row().prop(context.window_manager,
			'normtrans_bounds', 
			text='Bounds')
