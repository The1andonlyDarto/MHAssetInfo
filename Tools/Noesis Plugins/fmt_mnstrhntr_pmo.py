#Noesis Python model import+export test module, imports/exports some data from/to a made-up format

from inc_noesis import noesis
from inc_noesis import NoeBitStream
from inc_noesis import NoeMesh
from inc_noesis import NoeVec3
from inc_noesis import NoeVec4
from inc_noesis import NoeMat43
from inc_noesis import NoeModel
from inc_noesis import NoeVertWeight
from inc_noesis import rapi

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("Monster Hunter Portable Models", ".pmo")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel) #see also noepyLoadModelRPG

	noesis.logPopup()
	#print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
	return 1

PMO_HEADER = 0x006F6D70
PMO_VERSION = 0x00302E32

#check if it's this type based on the data
def noepyCheckType(data):
	if len(data) < 8:
		return 0
	bs = NoeBitStream(data)

	if bs.readInt() != PMO_HEADER:
		return 0
	if bs.readInt() != PMO_VERSION:
		return 0

	return 1

#load the model
def noepyLoadModel(data, mdlList):
	bs = NoeBitStream(data)
	if bs.readInt() != PMO_HEADER:
		return 0
	if bs.readInt() != PMO_VERSION:
		return 0

	filesize = bs.readUInt()
	scale = bs.readFloat()
	scalex = bs.readFloat()/scale
	scaley = bs.readFloat()/scale
	scalez = bs.readFloat()/scale
	uk_num1 = bs.readUShort()
	uk_numMeshes = bs.readUShort()

	sections = list()
	for _ in range(6):
		sections.append(bs.readUInt())

	#bs.seek(sections[0]) #some meta info

	bs.seek(sections[1])
	num_bones = []
	for _ in range(uk_numMeshes):
		bs.readUByte()
		num_bones.append(bs.readUByte())
		bs.readBytes(14)

	#bs.seek(sections[2]) #indices list

	bs.seek(sections[3])
	bones_map = []
	for meshi in range(uk_numMeshes):
		bones_map.append([])
		for _ in range(num_bones[meshi]):
			bs.readUByte()
			bones_map[meshi].append(bs.readUByte())

	bs.seek(sections[4])
	texture_map = []
	for _ in range(uk_numMeshes):
		bs.readInt()
		bs.readInt()
		texture_map.append(bs.readUInt())
		bs.readInt()
	# texture_map[2:6] = [1,2,0,3]

	bs.seek(sections[5])
	num_triangles = list()
	num_vertices = list()
	for _ in range(uk_numMeshes):
		num_vertices.append(bs.readUInt())
		num_triangles.append(bs.readUInt())
		bs.readInt()
		bs.readInt()

	meshes = []
	for meshi in range(uk_numMeshes):
		idxList = []
		posList = []
		normals = []
		uvs = []
		bdngwgts = []
		colors = []
		
		for _ in range(num_triangles[meshi]):
			idxList.append(bs.readUShort())
		
		for _ in range(num_vertices[meshi]):
			posList.append(NoeVec3((bs.readFloat()*scalex, bs.readFloat()*scaley, bs.readFloat()*scalez)))
			# posList.append(NoeVec3.fromBytes(bs.readBytes(12)))

			normal = []
			for _ in range(3):
				normal.append(bs.readUByte()/255.0)
			normals.append(NoeVec3(normal))
			bs.readByte()

			uv = []
			for _ in range(2):
				uv.append(bs.readUShort()/65535.0)
			uv.append(0.0)
			uvs.append(uv)

			wgts = []
			for _ in range(4):
				wgt = bs.readUShort()
				if wgt > 0:
					wgts.append(wgt/65535.0)

			idx = []
			for _ in range(len(wgts)):
				i = int(bs.readUByte()/3)
				# if i >= len(bones_map[meshi]):
				# 	print("{} out of range {} of mesh {}".format(i, len(bones_map[meshi]), meshi))
				idx.append(bones_map[meshi][i])
			bs.readBytes(4-len(wgts))
			bdngwgts.append(NoeVertWeight(idx, wgts))


		for j in idxList:
			if j >= len(posList):
				print("Index out of bound: {:X} in section {}".format(j,i))

		mesh = NoeMesh(idxList, posList, materialName="002_image_{:03}.pvr".format(texture_map[meshi]))
		mesh.normals += normals
		mesh.uvs += uvs
		mesh.weights += bdngwgts
		
		if meshi not in []:
			meshes.append(mesh)

	mdl = NoeModel(meshes)
	mdlList.append(mdl)			#important, don't forget to put your loaded model in the mdlList

	#this would be the default offset for quake models
	#rapi.setPreviewOption("setAngOfs", "0 180 0")
	return 1
