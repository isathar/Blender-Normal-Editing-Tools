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

import bpy, bmesh
from mathutils import Vector


# picks split/vertex normals from input data, applies custom normals to mesh
# returns true if normals were applied
def update_customnormals(mesh, normalslist):
	if len(normalslist) > 0:
		if mesh.use_auto_smooth:
			newnormslist = ()
			
			for f in normalslist:
				newnormslist = newnormslist + tuple(tuple(n) for n in f)
			
			mesh.calc_normals_split()
			
			for e in mesh.edges:
				e.use_edge_sharp = False
			
			mesh.validate(clean_customdata=False)
			mesh.normals_split_custom_set(newnormslist)
			mesh.free_normals_split()
			mesh.update()
			return True
			
		else:
			meshverts = []
			if bpy.context.mode == 'EDIT_MESH':
				bm = bmesh.from_edit_mesh(mesh)
				meshverts = [v for v in bm.verts]
				
				for i in range(len(meshverts)):
					meshverts[i].normal = normalslist[i].copy()
				
				bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)
				mesh.update()
			else:
				bm = bmesh.new()
				bm.from_mesh(mesh)
				meshverts = [v for v in bm.verts]
				
				for i in range(len(meshverts)):
					meshverts[i].normal = normalslist[i].copy()
				
				bm.to_mesh(mesh)
			
			del meshverts[:]
			return True
	
	return False


########################################
# Entry point for Generate functions:
class cust_normals_generate(bpy.types.Operator):
	bl_idname = 'object.cust_normals_generate'
	bl_label = 'Generate'
	bl_description = 'Generate normals'
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.window_manager.vn_normalsgenmode == 'DEFAULT':
					return bpy.ops.object.cust_normals_gendefault.poll()
				elif context.window_manager.vn_normalsgenmode == 'SMOOTH':
					return bpy.ops.object.cust_normals_gencustom.poll()
				elif context.window_manager.vn_normalsgenmode == 'WEIGHT':
					return bpy.ops.object.cust_normals_genweighted_area.poll()
				elif context.window_manager.vn_normalsgenmode == 'BENT':
					return bpy.ops.object.cust_normals_genbent.poll()
				elif context.window_manager.vn_normalsgenmode == 'FLAT':
					return bpy.ops.object.cust_normals_genflat.poll()
				elif context.window_manager.vn_normalsgenmode == 'TRANS':
					if context.active_object.data.use_auto_smooth:
						return bpy.ops.object.cust_normals_transfer_topoly.poll()
					else:
						return bpy.ops.object.cust_normals_transfer_tovert.poll()
		return False
	
	def execute(self, context):
		if context.window_manager.vn_normalsgenmode == 'DEFAULT':
			bpy.ops.object.cust_normals_gendefault({},'EXEC_DEFAULT',True)
		elif context.window_manager.vn_normalsgenmode == 'SMOOTH':
			bpy.ops.object.cust_normals_gencustom({},'EXEC_DEFAULT',True)
		elif context.window_manager.vn_normalsgenmode == 'WEIGHT':
			bpy.ops.object.cust_normals_genweighted_area({},'EXEC_DEFAULT',True)
		elif context.window_manager.vn_normalsgenmode == 'BENT':
			bpy.ops.object.cust_normals_genbent({},'EXEC_DEFAULT',True)
		elif context.window_manager.vn_normalsgenmode == 'FLAT':
			bpy.ops.object.cust_normals_genflat({},'EXEC_DEFAULT',True)
		elif context.window_manager.vn_normalsgenmode == 'TRANS':
			if context.active_object.data.use_auto_smooth:
				bpy.ops.object.cust_normals_transfer_topoly({},'EXEC_DEFAULT',True)
			else:
				bpy.ops.object.cust_normals_transfer_tovert({},'EXEC_DEFAULT',True)
		return {'FINISHED'}


#####################################
# Generation methods:

# - Default -
class cust_normals_gendefault(bpy.types.Operator):
	bl_idname = 'object.cust_normals_gendefault'
	bl_label = 'Default'
	bl_description = 'Generate default normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.use_auto_smooth:
					return context.mode == 'OBJECT'
				return True
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
			
			bpy.ops.object.shade_smooth()
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
			vertslist = []
			bm = None
			if context.mode == 'OBJECT':
				bm = bmesh.new()
				bm.from_mesh(mesh)
				vertslist = [v for v in bm.verts]
			elif context.mode == 'EDIT_MESH':
				bm = bmesh.from_edit_mesh(mesh)
				vertslist = [v for v in bm.verts]
			
			orignormals = []
			newnormals = []
			
			# get old normals
			for v in vertslist:
				orignormals.append(v.normal.copy())
			
			# recalc
			bm.normal_update()
			
			# get new normals list
			for v in vertslist:
				newnormals.append(v.normal.copy())
			
			# calculate ratio, write to mesh
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
			
			if context.mode == 'OBJECT':
				bm.to_mesh(mesh)
			else:
				bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)
			
			# cleanup
			del vertslist[:]
			del orignormals[:]
			del newnormals[:]
			
		context.area.tag_redraw()
		context.scene.update()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 
			'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 
			'vn_editselection', text='Selected Only')


# - Bent -
class cust_normals_genbent(bpy.types.Operator):
	bl_idname = 'object.cust_normals_genbent'
	bl_label = 'Bent'
	bl_description = 'Calculate normals bent away from 3d cursor'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.use_auto_smooth:
					return context.mode == 'OBJECT'
				return True
		return False
	
	def execute(self, context):
		editsplit = context.active_object.data.use_auto_smooth
		cursorloc = context.scene.cursor_location
		bendratio = abs(context.window_manager.vn_bendingratio)
		mesh = context.active_object.data
		
		# build lists
		normalsdata = []
		normalsdata_proc = []
		
		if editsplit:
			editselection = bpy.context.window_manager.vn_editselection
			selectByFace = bpy.context.window_manager.vn_editbyface
			
			mesh.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in mesh.vertices]
			loopnorms_raw = [(l.normal).copy() for l in mesh.loops]
			
			loopcount = 0
			
			for f in mesh.polygons:
				fvn = []
				fvco = []
				fvsel = []
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if editselection:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
				
				normalsdata.append([fvco,fvn,fvsel])
				normalsdata_proc.append(fvn)
			
			mesh.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
		else:
			editselection = bpy.context.window_manager.vn_editselection
			normalsdata = [[],[],[]]
			
			for v in mesh.vertices:
				normalsdata[0].append((v.co).copy())
				normalsdata[1].append((v.normal).copy())
				normalsdata_proc.append((v.normal).copy())
				if editselection:
					normalsdata[2].append(v.select)
				else:
					normalsdata[2].append(True)
		
		# calculate new normals
		if editsplit:
			for i in range(len(normalsdata)):
				for j in range(len(normalsdata[i][0])):
					if normalsdata[i][2][j]:
						tempv = (normalsdata[i][0][j] - cursorloc).normalized()
						tempv = normalsdata[i][1][j] * (1.0 - bendratio) + (tempv * bendratio)
						normalsdata_proc[i][j] = tempv.normalized()
		else:
			for i in range(len(normalsdata[0])):
				if normalsdata[2][i]:
					tempv = (normalsdata[0][i] - cursorloc).normalized()
					tempv = normalsdata[1][i] * (1.0 - bendratio) + (tempv * bendratio)
					normalsdata_proc[i] = tempv.normalized()
		
		# free some memory
		del normalsdata[:]
		
		# apply new normals to the mesh
		if (update_customnormals(mesh, normalsdata_proc)):
			context.area.tag_redraw()
			context.scene.update()
		
		# cleanup
		del normalsdata_proc[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')
		if context.active_object.data.use_auto_smooth:
			layout.column().prop(context.window_manager, 'vn_editbyface', text='Face Selection')


# - Smooth (Averaged) -
# TBD: add dot product range for automatic splits
class cust_normals_gencustom(bpy.types.Operator):
	bl_idname = 'object.cust_normals_gencustom'
	bl_label = 'Smooth'
	bl_description = 'Custom normals using averaged face normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.use_auto_smooth:
					return context.mode == 'OBJECT'
				return True
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.active_object.data.use_auto_smooth
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		bendratio = context.window_manager.vn_bendingratio
		
		mesh = context.active_object.data
		bm = None
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
		elif context.mode == 'OBJECT':
			bm = bmesh.new()
			bm.from_mesh(mesh)
		
		# build lists
		lfindex = []
		normalsdata = []
		normalsdata_proc = []
		
		if editsplit:
			mesh.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in mesh.vertices]
			loopnorms_raw = [(l.normal).copy() for l in mesh.loops]
			
			loopcount = 0
			
			for f in mesh.polygons:
				fvn = []
				fvco = []
				fvsel = []
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if showselected:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
				
				normalsdata.append([fvco,fvn,fvsel])
				normalsdata_proc.append(fvn)
			
			mesh.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
			faceslist = [f for f in bm.faces]
			lfindex = [[] for i in range(len(normalsdata))]
			
			for i in range(len(normalsdata)):
				for v in faceslist[i].verts:
					if showselected:
						if selectByFace:
							lfindex[i].append([[vf.normal, vf.select] for vf in v.link_faces])
						else:
							lfindex[i].append([[vf.normal, v.select] for vf in v.link_faces])
					else:
						lfindex[i].append([[vf.normal, True] for vf in v.link_faces])
			
			del faceslist[:]
		else:
			normalsdata = [[],[],[]]
			
			for v in mesh.vertices:
				normalsdata[0].append((v.co).copy())
				normalsdata[1].append((v.normal).copy())
				normalsdata_proc.append((v.normal).copy())
				if showselected:
					normalsdata[2].append(v.select)
				else:
					normalsdata[2].append(True)
			
			for v in bm.verts:
				if showselected:
					if selectByFace:
						lfindex.append([[vf.normal, vf.select] for vf in v.link_faces])
					else:
						lfindex.append([[vf.normal, v.select] for vf in v.link_faces])
				else:
					lfindex.append([[vf.normal, True] for vf in v.link_faces])
		
		# create new normals
		if editsplit:
			for i in range(len(normalsdata)):
				for j in range(len(normalsdata[i][1])):
					if normalsdata[i][2][j]:
						tempfvect = Vector((0.0,0.0,0.0))
						for vf in lfindex[i][j]:
							if vf[1]:
								tempfvect = tempfvect + vf[0].copy()
						
						tempv = (normalsdata[i][1][j] * (1.0 - bendratio)) + ((tempfvect).normalized() * bendratio)
						normalsdata_proc[i][j] = tempv.normalized()
			
		else:
			for i in range(len(normalsdata[1])):
				if normalsdata[2][i]:
					tempfvect = Vector((0.0,0.0,0.0))
					for j in range(len(lfindex[i])):
						if (lfindex[i][j][1]):
							tempfvect = tempfvect + (lfindex[i][j][0]).copy()
					
					tempv = (normalsdata[1][i] * (1.0 - bendratio)) + ((tempfvect).normalized() * bendratio)
					normalsdata_proc[i] = tempv.normalized()
		
		del lfindex[:]
		del normalsdata[:]
		
		# apply new normals to the mesh
		if (update_customnormals(mesh, normalsdata_proc)):
			context.area.tag_redraw()
			context.scene.update()
		
		# clean up
		del normalsdata_proc[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')


# - Weighted (face area / vertex) -
class cust_normals_genweighted_area(bpy.types.Operator):
	bl_idname = 'object.cust_normals_genweighted_area'
	bl_label = 'Weighted'
	bl_description = 'Custom normals using averaged face normals and face area weights'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.use_auto_smooth:
					return context.mode == 'OBJECT'
				return True
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.active_object.data.use_auto_smooth
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		bendratio = context.window_manager.vn_bendingratio
		
		mesh = context.active_object.data
		bm = None
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
		elif context.mode == 'OBJECT':
			bm = bmesh.new()
			bm.from_mesh(mesh)
			
		normalsdata = []
		normalsdata_proc = []
		lfindex = []
		
		# build lists
		if editsplit:
			mesh.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in mesh.vertices]
			loopnorms_raw = [(l.normal).copy() for l in mesh.loops]
			
			loopcount = 0
			
			for f in mesh.polygons:
				fvn = []
				fvco = []
				fvsel = []
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if showselected:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
				
				normalsdata.append([fvco,fvn,fvsel])
				normalsdata_proc.append(fvn)
			
			mesh.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
			faceslist = [f for f in bm.faces]
			lfindex = [[] for i in range(len(normalsdata))]
			
			for i in range(len(normalsdata)):
				for v in faceslist[i].verts:
					if showselected:
						if selectByFace:
							lfindex[i].append([[vf.normal, vf.select, vf.calc_area()] for vf in v.link_faces])
						else:
							lfindex[i].append([[vf.normal, v.select, vf.calc_area()] for vf in v.link_faces])
					else:
						lfindex[i].append([[vf.normal, True, vf.calc_area()] for vf in v.link_faces])
			
			del faceslist[:]
		else:
			normalsdata = [[],[],[]]
			
			for v in mesh.vertices:
				normalsdata[0].append((v.co).copy())
				normalsdata[1].append((v.normal).copy())
				normalsdata_proc.append((v.normal).copy())
				if showselected:
					normalsdata[2].append(v.select)
				else:
					normalsdata[2].append(True)
			
			for v in bm.verts:
				if showselected:
					lfindex.append([[vf.normal, v.select, vf.calc_area()] for vf in v.link_faces])
				else:
					lfindex.append([[vf.normal, True, vf.calc_area()] for vf in v.link_faces])
		
		# create new normals
		if editsplit:
			for i in range(len(normalsdata)):
				for j in range(len(normalsdata[i][1])):
					if normalsdata[i][2][j]:
						tempfvect = Vector((0.0,0.0,0.0))
						for vf in lfindex[i][j]:
							if vf[1]:
								tempfvect = tempfvect + (vf[0].copy() * vf[2])
						
						tempv = (normalsdata[i][1][j] * (1.0 - bendratio)) + ((tempfvect).normalized() * bendratio)
						normalsdata_proc[i][j] = tempv.normalized()
		else:
			for i in range(len(normalsdata[1])):
				if normalsdata[2][i]:
					tempfvect = Vector((0.0,0.0,0.0))
					for j in range(len(lfindex[i])):
						if (lfindex[i][j][1]):
							tempfvect = tempfvect + ((lfindex[i][j][0]).copy() * lfindex[i][j][2])
					
					tempv = (normalsdata[1][i] * (1.0 - bendratio)) + ((tempfvect).normalized() * bendratio)
					normalsdata_proc[i] = tempv.normalized()
		
		del lfindex[:]
		del normalsdata[:]
		
		# apply new normals to the mesh
		if (update_customnormals(mesh, normalsdata_proc)):
			context.area.tag_redraw()
			context.scene.update()
		
		# clean up
		del normalsdata_proc[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager, 'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager, 'vn_editselection', text='Selected Only')


# - Flat -
class cust_normals_genflat(bpy.types.Operator):
	bl_idname = 'object.cust_normals_genflat'
	bl_label = 'Flat'
	bl_description = 'Generate custom flat normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.use_auto_smooth:
					return context.mode == 'OBJECT'
		return False
	
	def execute(self, context):
		# gather vars
		bendratio = context.window_manager.vn_bendingratio
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		
		mesh = context.active_object.data
		mesh.update()
		mesh.calc_normals_split()
		
		# build lists
			
		vertslist = [[(v.co).copy(), v.select] for v in mesh.vertices]
		loopnorms_raw = [(l.normal).copy() for l in mesh.loops]
		
		loopcount = 0
		
		normalsdata = []
		normalsdata_proc = []
		
		for f in mesh.polygons:
			fvn = []
			fvco = []
			fvsel = []
			
			for v in f.vertices:
				fvco.append(vertslist[v][0].copy())
				fvn.append(loopnorms_raw[loopcount].copy())
				
				if showselected:
					if selectByFace:
						fvsel.append(f.select)
					else:
						fvsel.append(vertslist[v][1])
				else:
					fvsel.append(True)
				loopcount += 1
			
			normalsdata.append([fvco,fvn,fvsel])
			normalsdata_proc.append(fvn)
		
		mesh.free_normals_split()
		
		del vertslist[:]
		del loopnorms_raw[:]
		
		# create new normals
		fcount = 0
		if context.window_manager.vn_editselection:
			for f in mesh.polygons:
				for i in range(len(f.vertices)):
					if normalsdata[fcount][2][i]:
						normalsdata_proc[fcount][i] = (
							(normalsdata[fcount][1][i] 
							* (1.0 - bendratio)) 
							+ (f.normal.copy() 
							* bendratio)
						).normalized()
				fcount += 1
		else:
			for f in mesh.polygons:
				for i in range(len(f.vertices)):
					normalsdata_proc[fcount][i] = ((normalsdata[fcount][1][i] * (1.0 - bendratio)) + (f.normal.copy() * bendratio)).normalized()
				fcount += 1
		
		del normalsdata[:]
		
		# apply new normals to the mesh
		if (update_customnormals(mesh, normalsdata_proc)):
			context.area.tag_redraw()
			context.scene.update()
		
		# clean up
		del normalsdata_proc[:]
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager,
			'vn_bendingratio', text='Amount')
		layout.column().prop(context.window_manager,
			'vn_editselection', text='Selected Only')


# - Flip -
class cust_normals_flipdir(bpy.types.Operator):
	bl_idname = 'object.cust_normals_flipdir'
	bl_label = 'Flip'
	bl_description = 'Flip the direction of selected normals'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			if context.active_object.type == 'MESH':
				if context.active_object.data.use_auto_smooth:
					return context.mode == 'OBJECT'
				return True
		return False
	
	def execute(self, context):
		# gather vars
		editsplit = context.active_object.data.use_auto_smooth
		showselected = context.window_manager.vn_editselection
		
		mesh = context.active_object.data
		
		meshverts = []
		if context.mode == 'EDIT_MESH':
			bm = bmesh.from_edit_mesh(mesh)
			meshverts = [v for v in bm.verts]
		elif context.mode == 'OBJECT':
			bm = bmesh.new()
			bm.from_mesh(mesh)
			meshverts = [v for v in bm.verts]
		
		# build lists
		normalsdata = []
		normalsdata_proc = []
		
		if editsplit:
			mesh.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in mesh.vertices]
			loopnorms_raw = [(l.normal).copy() for l in mesh.loops]
			
			loopcount = 0
			
			for f in mesh.polygons:
				fvn = []
				fvco = []
				fvsel = []
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if showselected:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
				
				normalsdata.append([fvco,fvn,fvsel])
				normalsdata_proc.append(fvn)
			
			mesh.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
		else:
			normalsdata = [[],[],[]]
			
			for v in mesh.vertices:
				normalsdata[0].append((v.co).copy())
				normalsdata[1].append((v.normal).copy())
				normalsdata_proc.append((v.normal).copy())
				if showselected:
					normalsdata[2].append(v.select)
				else:
					normalsdata[2].append(True)
		
		
		# flip normals in list
		if editsplit:
			for i in range(len(normalsdata)):
				for j in range(len(normalsdata[i][1])):
					if normalsdata[i][2][j]:
						normalsdata_proc[i][j] = normalsdata[i][1][j] * -1.0
		else:
			for i in range(len(normalsdata[1])):
				if normalsdata[2][i]:
					normalsdata_proc[i] = normalsdata[1][i] * -1.0
		
		del normalsdata[:]
		
		# apply new normals to the mesh
		if (update_customnormals(mesh, normalsdata_proc)):
			context.area.tag_redraw()
			context.scene.update()
		
		# clean up
		del normalsdata_proc[:]
		
		return {'FINISHED'}


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
			if context.active_object:
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
			if context.active_object:
				if context.active_object.type == 'MESH':
					return context.active_object.data.use_auto_smooth
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
			tempv = Vector((0.0,0.0,0.0))
			for v in vl:
				tempv = tempv + v
			tempv = tempv.normalized()
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


#############################################################
# Manual editing

# create manipulator object
def CreateNormArrow(context):
	selObj = context.active_object
	
	if not ('NormDirAxis' in context.scene.objects):
		bpy.ops.object.empty_add(type='SINGLE_ARROW')
		tempDirObj = context.active_object
		tempDirObj.name = 'NormDirAxis'
		tempDirObj.empty_draw_size = context.window_manager.vn_editmode_arrowsize
		tempDirObj.rotation_mode = 'QUATERNION'
	
	if not ('NormDirEnd' in context.scene.objects):
		bpy.ops.object.empty_add(type='SPHERE')
		tempsphere = context.active_object
		tempsphere.name = 'NormDirEnd'
		tempsphere.location = (0.0,0.0,context.window_manager.vn_editmode_arrowsize)
		tempsphere.empty_draw_size = context.window_manager.vn_editmode_arrowsize * 0.15
		tempsphere.parent = tempDirObj
		
		tempsphere.select = False
		tempDirObj.select = False
	
	selObj.select = True
	context.scene.objects.active = selObj


# delete manipulator object
def ClearNormArrow(context):
	selObj = context.active_object
	
	for obj in context.scene.objects:
		if obj.select:
			obj.select = False
	
	if ('NormDirAxis' in context.scene.objects):
		tempDirObj = context.scene.objects['NormDirAxis']
		tempDirObj.select = True
		context.scene.objects.active = tempDirObj
		bpy.ops.object.delete(use_global=False)
	
	if ('NormDirEnd' in context.scene.objects):
		tempSphere = context.scene.objects['NormDirEnd']
		tempSphere.select = True
		context.scene.objects.active = tempSphere
		bpy.ops.object.delete(use_global=False)
	
	selObj.select = True
	context.scene.objects.active = selObj


# convert current manipulator rotation to normal
def CalcArrowNormDirection(context):
    v1 = context.scene.objects['NormDirAxis'].matrix_world.translation
    v2 = context.scene.objects['NormDirEnd'].matrix_world.translation
    return (v2 - v1).normalized()


# enable new editing mode
class cust_normals_enableediting(bpy.types.Operator):
	bl_idname = 'object.cust_normals_enableediting'
	bl_label = 'Enable Arrow'
	bl_description = 'Enable manual edit manipulator'
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'
	
	def execute(self, context):
		CreateNormArrow(context)
		context.window_manager.vn_editmode_enabled = True
		return {'FINISHED'}


# disable new editing mode
class cust_normals_disableediting(bpy.types.Operator):
	bl_idname = 'object.cust_normals_disableediting'
	bl_label = 'Disable Arrow'
	bl_description = 'Disable manual edit manipulator'
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'
	
	def execute(self, context):
		context.window_manager.vn_editmode_enabled = False
		ClearNormArrow(context)
		return {'FINISHED'}


# set normal(s) from manipulator rot
class cust_normals_manualset(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualset'
	bl_label = 'Set'
	bl_description = 'Set selected vertex normals from arrow'
	bl_options = {'REGISTER','UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		editarrow = context.window_manager.vn_editmode_enabled
		tempnorm = context.window_manager.vn_dirvector
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		
		objdata = context.active_object.data
		
		if context.active_object.data.use_auto_smooth:
			tempdata = []
			tempnormals = []
			
			objdata.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in objdata.vertices]
			loopnorms_raw = [(l.normal).copy() for l in objdata.loops]
			
			loopcount = 0
			
			for f in objdata.polygons:
				fvn = []
				fvco = []
				fvsel = []
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if showselected:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
				
				tempdata.append([fvco,fvn,fvsel])
				tempnormals.append(fvn)
			
			objdata.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
			if len(tempdata) > 0:
				fcount = 0
				for f in tempdata:
					for i in range(len(f[0])):
						if f[2][i]:
							if editarrow:
								tempnormals[fcount][i] = CalcArrowNormDirection(context)
							else:
								tempnormals[fcount][i] = tempnorm
					fcount += 1
				
				if (update_customnormals(objdata, tempnormals)):
					context.area.tag_redraw()
					context.scene.update()
			
			del tempdata[:]
			del tempnormals[:]
			
		else:
			bm = bmesh.new()
			bm.from_mesh(objdata)
			
			sourceverts = [v for v in bm.verts]
			if len(sourceverts) > 0:
				for v in sourceverts:
					if v.select:
						if editarrow:
							v.normal = CalcArrowNormDirection(context)	
						else:
							v.normal = tempnorm
				
				bm.to_mesh(objdata)
			
			del sourceverts[:]
		
		context.area.tag_redraw()
		context.scene.update()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager,
			'vn_dirvector', text='New Normal')


# get normal + apply to manipulator as rot
class cust_normals_manualget(bpy.types.Operator):
	bl_idname = 'object.cust_normals_manualget'
	bl_label = 'Get'
	bl_description = 'Get selected normal'
	bl_options = {'REGISTER','UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		editarrow = context.window_manager.vn_editmode_enabled
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		
		arrowobj = None
		if editarrow:
			arrowobj = context.scene.objects['NormDirAxis']
		
		objdata = context.active_object.data
		
		if context.active_object.data.use_auto_smooth:
			tempdata = []
			
			objdata.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in objdata.vertices]
			loopnorms_raw = [(l.normal).copy() for l in objdata.loops]
			
			loopcount = 0
			
			for f in objdata.polygons:
				fvn = []
				fvco = []
				fvsel = []
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if showselected:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
				
				tempdata.append([fvco,fvn,fvsel])
			
			objdata.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
			if len(tempdata) > 0:
				for f in tempdata:
					for i in range(len(f[0])):
						if f[2][i]:
							if editarrow:
								arrowobj.rotation_quaternion = (f[1][i]).to_track_quat('Z','Y')
							context.window_manager.vn_dirvector = (f[1][i]).copy()
							break
			del tempdata[:]
			
		else:
			sourceverts = [v for v in objdata.vertices]
			
			if len(sourceverts) > 0:
				for v in sourceverts:
					if v.select:
						if editarrow:
							arrowobj.rotation_quaternion = (v.normal).to_track_quat('Z','Y')
						context.window_manager.vn_dirvector = (v.normal).copy()
						break
			
			del sourceverts[:]
		
		context.area.tag_redraw()
		context.scene.update()
		
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.column().prop(context.window_manager,
			'vn_dirvector', text='Selected Normal')

###############################################################################
# Transfer

#######################
# Transfer Normals - vertex normals destination
class cust_normals_transfer_tovert(bpy.types.Operator):
	bl_idname = 'object.cust_normals_transfer_tovert'
	bl_label = 'Transfer'
	bl_description = 'Transfer normals from selected to active object (vertex)'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		influenceamount = abs(context.window_manager.vn_bendingratio)
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		
		maxdist = context.window_manager.normtrans_maxdist
		influencemult = 1.0 if (
			context.window_manager.vn_bendingratio > 0.0
		) else -1.0
		
		if maxdist <= 0.0:
			maxdist = 8192.0
		if influenceamount > 0.0:
			destobj = context.active_object.data
			
			destdata = [[],[],[]]
			
			for v in destobj.vertices:
				destdata[0].append((v.co).copy())
				destdata[1].append((v.normal).copy())
				if showselected:
					destdata[2].append(v.select)
				else:
					destdata[2].append(True)
			
			newnormals = [[] for v in destdata[1]]
			selobjects = [obj.data for obj in context.selected_objects if obj.type == 'MESH']
			
			sourceverts = []
			foundobj = (len(selobjects) > 1)
			
			for objmesh in selobjects:
				if objmesh != destobj:
					if objmesh.use_auto_smooth:
						sourceverts = []
						
						objmesh.calc_normals_split()
			
						vertslist = [[(v.co).copy(), v.select] for v in objmesh.vertices]
						loopnorms_raw = [(l.normal).copy() for l in objmesh.loops]
						
						loopcount = 0
						
						for f in objmesh.polygons:
							fvn = []
							fvco = []
							fvsel = []
							
							for v in f.vertices:
								fvco.append(vertslist[v][0].copy())
								fvn.append(loopnorms_raw[loopcount].copy())
								
								if showselected:
									if selectByFace:
										fvsel.append(f.select)
									else:
										fvsel.append(vertslist[v][1])
								else:
									fvsel.append(True)
								loopcount += 1
							
							sourceverts.append([fvco,fvn,fvsel])
						
						objmesh.free_normals_split()
						
						del vertslist[:]
						del loopnorms_raw[:]
						
						
						if len(sourceverts) > 0:
							vcount = 0
							for j in range(len(destdata[0])):
								nearest = (destdata[1][j]).copy()
								lastdist = maxdist
								if destdata[2][j]:
									for f in sourceverts:
										for i in range(len(f[0])):
											curdistv = destdata[0][j] - f[0][i]
											curdist = curdistv.magnitude
											
											if curdist < maxdist:
												if curdist < lastdist:
													nearest = (f[1][i]).copy()
													lastdist = curdist
									
									tempv = (
										((destdata[1][j] * (1.0 - influenceamount)) 
										+ (nearest * influenceamount))
										* influencemult
									).normalized()
									newnormals[vcount].append(tempv)
								else:
									newnormals[vcount].append((destdata[1][j]).copy())
								
								vcount += 1
							
							del sourceverts[:]
					else:
						sourceverts = [[],[],[]]
			
						for v in objmesh.vertices:
							sourceverts[0].append((v.co).copy())
							sourceverts[1].append((v.normal).copy())
							if showselected:
								sourceverts[2].append(v.select)
							else:
								sourceverts[2].append(True)
						
						if len(sourceverts) > 0:
							vcount = 0
							for j in range(len(destdata[0])):
								nearest = (destdata[1][j]).copy()
								lastdist = maxdist
								if destdata[2][j]:
									for i in range(len(sourceverts[0])):
										curdistv = destdata[0][j] - sourceverts[0][i]
										curdist = curdistv.magnitude
										
										if curdist < maxdist:
											if curdist < lastdist:
												nearest = (sourceverts[1][i]).copy()
												lastdist = curdist
									
									tempv = (
										((destdata[1][j] * (1.0 - influenceamount)) 
										+ (nearest * influenceamount))
										* influencemult
									).normalized()
									newnormals[vcount].append(tempv)
								else:
									newnormals[vcount].append((destdata[1][j]).copy())
								
								vcount += 1
							
							del sourceverts[:]
			
			del destdata[:]
			
			del selobjects[:]
			
			if foundobj:
				# average influences
				procnormslist = []
				for vl in newnormals:
					tempv = Vector((0.0,0.0,0.0))
					if len(vl) > 0:
						for v in vl:
							tempv = tempv + v
						procnormslist.append(tempv.normalized())
				
				if (update_customnormals(destobj, procnormslist)):
					context.area.tag_redraw()
					context.scene.update()
				
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
		layout.column().prop(context.window_manager,
			'vn_editselection', text='Selected Only')


#######################
# Transfer Normals - split normals destination
class cust_normals_transfer_topoly(bpy.types.Operator):
	bl_idname = 'object.cust_normals_transfer_topoly'
	bl_label = 'Transfer'
	bl_description = 'Transfer normals from selected to active object (split)'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == 'OBJECT':
			if context.active_object:
				return context.active_object.type == 'MESH'
		return False
	
	def execute(self, context):
		influenceamount = abs(context.window_manager.vn_bendingratio)
		showselected = context.window_manager.vn_editselection
		selectByFace = context.window_manager.vn_editbyface
		
		maxdist = context.window_manager.normtrans_maxdist
		influencemult = 1.0 if (
			context.window_manager.vn_bendingratio > 0.0
		) else -1.0
		
		selectByFace = context.window_manager.vn_editbyface
		editselection = context.window_manager.vn_editselection
		
		if maxdist <= 0.0:
			maxdist = 8192.0
		if influenceamount > 0.0:
			destobj = context.active_object.data
			destdata = []
			newnormals = []
			
			destobj.calc_normals_split()
			
			vertslist = [[(v.co).copy(), v.select] for v in destobj.vertices]
			loopnorms_raw = [(l.normal).copy() for l in destobj.loops]
			
			loopcount = 0
			dfcount = 0
			for f in destobj.polygons:
				fvn = []
				fvco = []
				fvsel = []
				newnormals.append([])
				
				for v in f.vertices:
					fvco.append(vertslist[v][0].copy())
					fvn.append(loopnorms_raw[loopcount].copy())
					
					if showselected:
						if selectByFace:
							fvsel.append(f.select)
						else:
							fvsel.append(vertslist[v][1])
					else:
						fvsel.append(True)
					loopcount += 1
					
					newnormals[dfcount].append([])
				
				destdata.append([fvco,fvn,fvsel])
				
				dfcount += 1
			
			destobj.free_normals_split()
			
			del vertslist[:]
			del loopnorms_raw[:]
			
			selobjects = [obj.data for obj in context.selected_objects if obj.type == 'MESH']
			sourceverts = []
			
			foundobj = (len(selobjects) > 1)
			
			for objmesh in selobjects:
				if objmesh != destobj:
					fcount = 0
					lastdist = maxdist
					curdistv = Vector((0.0,0.0,0.0))
					tempv = Vector((0.0,0.0,0.0))
					curdist = 0.0
					
					if objmesh.use_auto_smooth:
						sourceverts = []
						
						objmesh.calc_normals_split()
						
						vertslist = [[(v.co).copy(), v.select] for v in objmesh.vertices]
						loopnorms_raw = [(l.normal).copy() for l in objmesh.loops]
						
						loopcount = 0
						
						for f in objmesh.polygons:
							fvn = []
							fvco = []
							fvsel = []
							
							for v in f.vertices:
								fvco.append(vertslist[v][0].copy())
								fvn.append(loopnorms_raw[loopcount].copy())
								
								if showselected:
									if selectByFace:
										fvsel.append(f.select)
									else:
										fvsel.append(vertslist[v][1])
								else:
									fvsel.append(True)
								loopcount += 1
							
							sourceverts.append([fvco,fvn,fvsel])
						
						objmesh.free_normals_split()
						
						del vertslist[:]
						del loopnorms_raw[:]
						
						if len(sourceverts) > 0:
							for f in destdata:
								for i in range(len(f[0])):
									lastdist = maxdist
									nearest = f[1][i].copy()
									
									if f[2][i]:
										for df in sourceverts:
											for j in range(len(df[0])):
												curdistv = f[0][i] - df[0][j]
												curdist = curdistv.magnitude
												if curdist < maxdist:
													if curdist < lastdist:
														nearest = df[1][j].copy()
														lastdist = curdist
										
										tempv = (
											((f[1][i] * (1.0 - influenceamount)) 
											+ (nearest * influenceamount))
											* influencemult
										).normalized()
										newnormals[fcount][i].append(tempv.copy())
									
									else:
										newnormals[fcount][i].append(f[1][i].copy())
								
								fcount += 1
							
							del sourceverts[:]
					else:
						sourceverts = [[],[],[]]
			
						for v in objmesh.vertices:
							sourceverts[0].append((v.co).copy())
							sourceverts[1].append((v.normal).copy())
							if showselected:
								sourceverts[2].append(v.select)
							else:
								sourceverts[2].append(True)
						
						if len(sourceverts) > 0:
							
							for f in destdata:
								for i in range(len(f[0])):
									lastdist = maxdist
									nearest = f[1][i].copy()
									
									if f[2][i]:
										for j in range(len(sourceverts[0])):
											curdistv = f[0][i] - sourceverts[0][j]
											curdist = curdistv.magnitude
											if curdist < maxdist:
												if curdist < lastdist:
													nearest = sourceverts[1][j].copy()
													lastdist = curdist
										
										tempv = (
											((f[1][i] * (1.0 - influenceamount)) 
											+ (nearest * influenceamount))
											* influencemult
										).normalized()
										newnormals[fcount][i].append(tempv.copy())
									
									else:
										newnormals[fcount][i].append(f[1][i].copy())
								
								fcount += 1
							
							del sourceverts[:]
			
			del destdata[:]
			del selobjects[:]
			
			if foundobj:
				procnormslist = []
				
				for i in range(len(newnormals)):
					procnormslist.append([])
					for j in range(len(newnormals[i])):
						tempv = Vector((0.0,0.0,0.0))
						if len(newnormals[i][j]) > 0:
							for v in newnormals[i][j]:
								tempv = tempv + v
							procnormslist[i].append(tempv.normalized())
				
				if (update_customnormals(destobj, procnormslist)):
					context.area.tag_redraw()
					context.scene.update()
				
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
		layout.column().prop(context.window_manager,
			'vn_editselection', text='Selected Only')
		

