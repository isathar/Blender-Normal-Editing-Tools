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

#######################################
#	Normals Editor Functions + Classes

import bpy, bmesh
from math import pi
from mathutils import Vector


#####################################
# Generation methods:

# - Bent -
class cust_normals_genbent(bpy.types.Operator):
	bl_idname = 'object.cust_normals_genbent'
	bl_label = 'Bent'
	bl_description = 'Calculate normals bent towards/away from 3d cursor'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.data.use_auto_smooth:
				if context.mode == 'OBJECT':
					return context.active_object.type == 'MESH'
			else:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.active_object.data.use_auto_smooth
		showselected = context.window_manager.vn_editselection
		
		mesh = context.active_object.data
		mesh.update()
		
		meshverts = []
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
			meshverts = [v for v in bm.verts]
		elif context.mode == 'OBJECT':
			meshverts = [v for v in mesh.vertices]
		
		# build lists
		normslist = []
		selectedlist = []
		locslist = []
		
		if editsplit:
			mesh.calc_normals_split()
			loopnorms = [v.normal.copy() for v in mesh.loops]
			
			loopcount = 0
			for f in mesh.polygons:
				fvns = []
				for i in range(len(f.vertices)):
					fvns.append(loopnorms[loopcount].copy())
					loopcount += 1
				normslist.append(fvns)
				if showselected:
					selectedlist.append(f.select)
				locslist.append([(meshverts[v].co).copy() for v in f.vertices])
			
			del loopnorms[:]
		else:
			for v in meshverts:
				normslist.append(v.normal.copy())
				if showselected:
					selectedlist.append(v.select)
				locslist.append(v.co.copy())
		
		# calculate new normals
		cursorloc = context.scene.cursor_location
		bendratio = abs(context.window_manager.vn_bendingratio)
		
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
				for i in range(len(meshverts)):
					meshverts[i].normal = normslist[i].copy()
				
				bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)
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
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')
	
	

# - Smooth (weighted by number of verts) -
# - TBD: re-add angle limits for angle-based edge splits
class cust_normals_gencustom(bpy.types.Operator):
	bl_idname = 'object.cust_normals_gencustom'
	bl_label = 'Smooth'
	bl_description = 'Generate custom smooth normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.data.use_auto_smooth:
				if context.mode == 'OBJECT':
					return context.active_object.type == 'MESH'
			else:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.active_object.data.use_auto_smooth
		showselected = context.window_manager.vn_editselection
		mesh = context.active_object.data
		
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
				bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)
				mesh.update()
			else:
				mesh.update()
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
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')


# - Default -
class cust_normals_gendefault(bpy.types.Operator):
	bl_idname = 'object.cust_normals_gendefault'
	bl_label = 'Default'
	bl_description = 'Generate default normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.data.use_auto_smooth:
				if context.mode == 'OBJECT':
					return context.active_object.type == 'MESH'
			else:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		bendratio = context.window_manager.vn_bendingratio
		
		# using split normals
		if context.active_object.data.use_auto_smooth:
			tempverts = [v.select for v in mesh.vertices]
			
			mesh.calc_normals_split()
			# get old normals
			oldloopnorms = [v.normal.copy() for v in mesh.loops]
			
			# reset/generate default normals
			for e in mesh.edges:
				e.use_edge_sharp = False
			mesh.validate(clean_customdata=False)
			clearlist = tuple(tuple([0.0,0.0,0.0]) for i in range(len(mesh.vertices)))
			mesh.normals_split_custom_set_from_vertices(clearlist)
			mesh.free_normals_split()
			
			#mesh.calc_normals()
			mesh.calc_normals_split()
			mesh.update()
			
			newloopnorms = [v.normal.copy() for v in mesh.loops]
			finalnorms = []
			
			lcount = 0
			if context.window_manager.vn_editselection:
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
			# create lists
			vertslist = [v for v in mesh.vertices]
			orignormals = []
			newnormals = []
			
			# get old normals
			for v in vertslist:
				orignormals.append(v.normal.copy())
			# recalc
			mesh.calc_normals()
			mesh.update()
			# get new normals
			for v in vertslist:
				newnormals.append(v.normal.copy())
			
			# calculate, write to mesh
			mesh.update()
			vcount = 0
			if context.window_manager.vn_editselection:
				for v in vertslist:
					if v.select:
						v.normal = ((orignormals[vcount] * (1.0 - bendratio)) + (newnormals[vcount] * bendratio)).normalized()
					else:
						v.normal = orignormals[vcount]
					vcount += 1
			else:
				for v in vertslist:
					tempv = ((orignormals[vcount] * (1.0 - bendratio)) + (newnormals[vcount] * bendratio)).normalized()
					v.normal = tempv.copy()
					vcount += 1
			
			# cleanup
			del vertslist[:]
			del orignormals[:]
			del newnormals[:]
			
		context.area.tag_redraw()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 
			'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 
			'vn_editselection', text='Selected Only')


# - Flat -
class cust_normals_genflat(bpy.types.Operator):
	bl_idname = 'object.cust_normals_genflat'
	bl_label = 'Flat'
	bl_description = 'Generate custom flat normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.mode == 'OBJECT' and context.active_object.data.use_auto_smooth:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		# gather vars
		bendratio = context.window_manager.vn_bendingratio
		
		mesh = context.active_object.data
		mesh.update()
		mesh.calc_normals_split()
		
		# build lists
		normslist = []
		loopnorms = [v.normal for v in mesh.loops]
		loopcount = 0
		for f in mesh.polygons:
			fvns = []
			for i in range(len(f.vertices)):
				fvns.append(loopnorms[loopcount].copy())
				loopcount += 1
			normslist.append(fvns)
		del loopnorms[:]
		
		# create new normals
		fcount = 0
		if context.window_manager.vn_editselection:
			for f in mesh.polygons:
				if f.select:
					for i in range(len(f.vertices)):
						normslist[fcount][i] = (
							(normslist[fcount][i] 
							* (1.0 - bendratio)) 
							+ (f.normal.copy() 
							* bendratio)
						).normalized()
				fcount += 1
		else:
			for f in mesh.polygons:
				for i in range(len(f.vertices)):
					normslist[fcount][i] = ((normslist[fcount][i] * (1.0 - bendratio)) + (f.normal.copy() * bendratio)).normalized()
				fcount += 1
		
		# convert temp normals list to tuples
		newnormslist = ()
		for f in normslist:
			newnormslist = newnormslist + tuple(tuple(n) for n in f)
		
		# apply new normals to the mesh
		for e in mesh.edges:
			e.use_edge_sharp = False
		mesh.validate(clean_customdata=False)
		mesh.normals_split_custom_set(newnormslist)
		mesh.free_normals_split()
		mesh.update()
		
		# clean up
		del normslist[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager,
			'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager,
			'vn_editselection', text='Selected Only')



####################################
# Editor Mode Switching

# -	Vert -> Split -
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
			if e.use_edge_sharp:
				e.use_edge_sharp = False
		
		mesh.create_normals_split()
		mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
		mesh.validate(clean_customdata=False)
		if not mesh.use_auto_smooth:
			mesh.use_auto_smooth = True
		if not mesh.show_edge_sharp:
			mesh.show_edge_sharp = True
		mesh.normals_split_custom_set_from_vertices(newnormslist)
		mesh.free_normals_split()
		mesh.update()
		
		
		return {'FINISHED'}

# -	Split -> Vert -
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
		
		mesh.update()
		mesh.calc_normals_split()
		
		# store old normals
		normslist = []
		loopnorms = [v.normal for v in mesh.loops]
		loopcount = 0
		for f in mesh.polygons:
			fvns = []
			for i in range(len(f.vertices)):
				fvns.append(loopnorms[loopcount].copy())
				loopcount += 1
			normslist.append(fvns)
		del loopnorms[:]
		
		# clear old normals
		emptynormslist = tuple(tuple((0,0,0)) for v in mesh.vertices)
		for e in mesh.edges:
			if e.use_edge_sharp:
				e.use_edge_sharp = False
		
		mesh.validate(clean_customdata=False)
		if mesh.use_auto_smooth:
			mesh.use_auto_smooth = False
		if mesh.show_edge_sharp:
			mesh.show_edge_sharp = False
		mesh.normals_split_custom_set_from_vertices(emptynormslist)
		mesh.free_normals_split()
		mesh.update()
		
		# gather old split normals
		rawnormslist = [[] for v in mesh.vertices]
		
		faceslist = [f for f in mesh.polygons]
		fcount = 0
		for f in faceslist:
			newfn = []
			vcount = 0
			for v in f.vertices:
				rawnormslist[v].append(normslist[fcount][vcount])
				vcount += 1
			fcount += 1
		
		# average split normals for new list
		procnormslist = []
		for vl in rawnormslist:
			avgcount = len(vl)
			tempv = Vector((0.0,0.0,0.0))
			if avgcount > 0:
				for v in vl:
					tempv = tempv + v
				tempv = tempv / avgcount
			procnormslist.append(tempv)
		
		vertslist = [v for v in mesh.vertices]
		vcount = 0
		for v in vertslist:
			v.normal = procnormslist[vcount]
			vcount += 1
		
		
		del rawnormslist[:]
		del procnormslist[:]
		del faceslist[:]
		del vertslist[:]
		
		return {'FINISHED'}


#####################
# Manual set/get
# - 2 functions for now to work around undo issue

# - Set (Vertex Mode) -
class cust_normals_manualset_vert(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualset_vert'
	bl_label = 'Set'
	bl_description = 'Set selected vertex normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if not context.active_object.data.use_auto_smooth:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		mesh = context.active_object.data
		mesh.update()
		newnorm = context.window_manager.vn_dirvector
		
		vertslist = []
		
		bm = ''
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
			vertslist = [v for v in bm.verts]
		elif context.mode == 'OBJECT':
			vertslist = [v for v in mesh.vertices]
		
		if context.window_manager.vn_editselection:
			for v in vertslist:
				if v.select:
					v.normal = newnorm
		else:
			for v in vertslist:
				v.normal = newnorm
		
		if context.mode == 'EDIT_MESH':
			bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)
			mesh.update()
		
		del vertslist[:]
		
		context.area.tag_redraw()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager,
			'vn_dirvector', text='New Normal')
		layout.column().prop(context.window_manager,
			'vn_editselection', text='Selected Only')


# - Set (Split Mode) -
class cust_normals_manualset_poly(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualset_poly'
	bl_label = 'Set'
	bl_description = 'Set selected vertex normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.data.use_auto_smooth:
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
		layout.column().prop(context.window_manager,
			'vn_dirvector', text='New Normal')
		layout.column().prop(context.window_manager,
			'vn_selected_face', text='Face Index')
		layout.column().prop(context.window_manager,
			'vn_editselection', text='Selected Only')


# - Get -
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
		
		if context.active_object.data.use_auto_smooth:
			normslist = []
			selfaces = []
			selverts = []
			
			mesh.calc_normals_split()
			loopnorms = [v.normal.copy() for v in mesh.loops]
			mesh.free_normals_split()
			
			bm = bmesh.new()
			bm.from_mesh(mesh)
			
			mesh.update()
			
			loopcount = 0
			for f in mesh.polygons:
				fvns = []
				for i in range(len(f.vertices)):
					fvns.append(loopnorms[loopcount].copy())
					loopcount += 1
				normslist.append(fvns)
			del loopnorms[:]
			
			fcount = 0
			selectedface = context.window_manager.vn_selected_face
			if selectedface < 0:
				context.window_manager.vn_selected_face = 0
				selectedface = 0
			
			vertslist = [v for v in bm.verts]
			for v in vertslist:
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
				context.window_manager.vn_dirvector = normslist[
					selfaces[selectedface]][selverts[selectedface]]
			
			del selfaces[:]
			del selverts[:]
			del normslist[:]
			del vertslist[:]
		else:
			vertslist = []
			
			if context.mode == 'EDIT_MESH':
				bm = bmesh.from_edit_mesh(mesh)
				vertslist = [v.normal for v in bm.verts if v.select]
			elif context.mode == 'OBJECT':
				vertslist = [v.normal for v in mesh.vertices if v.select]
			
			if len(vertslist) > 0:
				context.window_manager.vn_dirvector = vertslist[0]
			
			del vertslist[:]
			
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		vecrow = layout.column()
		vecrow.prop(context.window_manager,
			'vn_dirvector', text='Current Normal')
		vecrow.enabled = False
		layout.row().prop(context.window_manager,
			'vn_selected_face', text='Face Index')


#######################
# Transfer Normals
class cust_normals_transfer_tovert(bpy.types.Operator):
	bl_idname = 'object.cust_normals_transfer_tovert'
	bl_label = 'Transfer'
	bl_description = 'Transfer normals from selected to active object'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		# limited to 8192 since float_info.max threw errors in old falloff calc
		fmax = 8192.0
		
		totalinfluence = abs(context.window_manager.vn_bendingratio)
		influenceamount = abs(context.window_manager.vn_bendingratio)
		
		maxdist = context.window_manager.normtrans_maxdist
		influencemult = 1.0 if (
			context.window_manager.vn_bendingratio > 0.0
		) else -1.0
		
		if maxdist <= 0.0:
			maxdist = fmax
		if influenceamount > 0.0:
			destobj = context.active_object.data
			destobj.update()
			
			destdata = [[
					(v.co).copy(),
					(v.normal).copy()
				] for v in destobj.vertices
			]
			
			testselverts = [
				v.select for v in destobj.vertices
			] if context.window_manager.vn_editselection else [
				True for v in destobj.vertices]
			
			newnormals = [[] for i in range(len(destobj.vertices))]
			selobjects = [obj for obj in context.selected_objects]
			
			sourceverts = []
			foundobj = False
			
			for obj in selobjects:
				if obj.type == 'MESH':
					objmesh = obj.data
					if objmesh != destobj:
						foundobj = True
						sourceverts = [[
								(v.co).copy(),
								(v.normal).copy()
							] for v in objmesh.vertices
						]
						
						if len(sourceverts) > 0:
							vcount = 0
							
							for v in destdata:
								nearest = v[1].copy()
								lastdist = maxdist
								if testselverts[vcount]:
									for dv in sourceverts:
										curdistv = v[0] - dv[0]
										curdist = curdistv.magnitude
										influenceamount = totalinfluence
										
										if curdist < maxdist:
											if curdist < lastdist:
												nearest = dv[1].copy()
												lastdist = curdist
									
									tempv = (
										((v[1] * (1.0 - influenceamount)) 
										+ (nearest * influenceamount))
										* influencemult
									).normalized()
									newnormals[vcount].append(tempv)
								else:
									newnormals[vcount].append(v[0].copy())
								vcount += 1
			
			del destdata[:]
			del sourceverts[:]
			del selobjects[:]
			
			if foundobj:
				# average influences
				procnormslist = []
				for vl in newnormals:
					tempv = Vector((0.0,0.0,0.0))
					if len(vl) > 0:
						for v in vl:
							tempv = tempv + v
						procnormslist.append((tempv / len(vl)).normalized())
				
				destverts = [v for v in destobj.vertices]
				# write to split normals if enabled
				# - temp, rewrite for actual split normals support pending
				if context.active_object.data.use_auto_smooth:
					newnormslist = tuple(tuple(v) for v in procnormslist)
					
					for e in destobj.edges:
						e.use_edge_sharp = False
					
					destobj.calc_normals_split()
					destobj.validate(clean_customdata=False)
					destobj.normals_split_custom_set_from_vertices(newnormslist)
					destobj.free_normals_split()
					destobj.update()
				else:
					vcount = 0
					for v in destverts:
						v.normal = procnormslist[vcount]
						vcount += 1
					
				context.area.tag_redraw()
				
				del destverts[:]
				del procnormslist[:]
			else:
				print('Need more than one object')
				
			del newnormals[:]
			
		else:
			print('No influence')
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.row().prop(context.window_manager,
			'vn_bendingratio', text='Ratio')
		layout.row().prop(context.window_manager,
			'normtrans_maxdist', text='Distance')
		

###############################################
# import saved normals used by other addons:

# - UDK FBX Tools -
class cust_normals_readfbxtools(bpy.types.Operator):
	bl_idname = 'object.cust_normals_readfbxtools'
	bl_label = 'FBX Tools'
	bl_description = 'Reads normals from data in a mesh saved with UE FBX Tools'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		
		return {'FINISHED'}

# - Recalc Vertex Normals -
class cust_normals_readadsnaddon(bpy.types.Operator):
	bl_idname = 'object.cust_normals_readadsnaddon'
	bl_label = 'Recalc Vertex Normals'
	bl_description = 'Reads normals from data in a mesh saved with Recalc Vertex Normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object != None:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		
		return {'FINISHED'}

