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
	handle = noesis.register("Monster Hunter Portable Skeleton", ".bin")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel) #see also noepyLoadModelRPG

	noesis.logPopup()
	#print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
	return 1

PMO_HEADER = 0xC0000000

#check if it's this type based on the data
def noepyCheckType(data):
	if len(data) < 8:
		return 0
	bs = NoeBitStream(data)

	if bs.readUInt() != PMO_HEADER:
		return 0

	return 1

#load the model
def noepyLoadModel(data, mdlList):
	bs = NoeBitStream(data)
	if bs.readUInt() != PMO_HEADER:
		return 0

	num_sections = bs.readUInt()-1
	filesize = bs.readUInt()
	bs.readInt()

	section0 = bs.readInt()
	if section0 == 1:
		bs.readBytes(8)
	elif section0 == 2:
		bs.readBytes(12)

	idxList = []
	posList = []
	for _ in range(num_sections):
		assert bs.readUInt() == 0x40000001
		assert bs.readUInt() == 0x1
		assert bs.readUInt() == 0x10C
		nodei = bs.readInt()
		parent = bs.readInt()
		lchild = bs.readInt()
		rsibling = bs.readInt()

		bs.readBytes(4*8)
		mat43 = []
		for _ in range(3):
			mat43.append(bs.readFloat())
		bs.readFloat()
		bs.readBytes(16*12)

		if parent == -1:
			pos = (0,0,0)
		else:
			pos = posList[parent].vec3
			idxList += (nodei, parent, parent)
		
		# transform = [0,0,0]
		# transform[0] += mat43[0]*pos[0]
		# transform[1] += mat43[1]*pos[0]
		# transform[2] += mat43[2]*pos[0]
		# transform[0] += mat43[3]*pos[1]
		# transform[1] += mat43[4]*pos[1]
		# transform[2] += mat43[5]*pos[1]
		# transform[0] += mat43[6]*pos[2]
		# transform[1] += mat43[7]*pos[2]
		# transform[2] += mat43[8]*pos[2]
		# transform[0] += mat43[9]
		# transform[1] += mat43[10]
		# transform[2] += mat43[11]
		# print(transform)
		transform = list(pos)
		transform[0] += mat43[0]
		transform[1] += mat43[1]
		transform[2] += mat43[2]
		print(mat43, transform)
		posList.append(NoeVec3(transform))

	mesh = NoeMesh(idxList, posList)
	mdl = NoeModel([mesh])
	mdlList.append(mdl)			#important, don't forget to put your loaded model in the mdlList

	#this would be the default offset for quake models
	#rapi.setPreviewOption("setAngOfs", "0 180 0")
	return 1
