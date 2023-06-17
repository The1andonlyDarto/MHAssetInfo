from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Monster Hunter World TEX Images", ".tex")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
	#noesis.logPopup()
	return 1

def noepyCheckType(data):
	bs = NoeBitStream(data)
	Magic = bs.readBytes(5)
	if Magic != b'\x54\x45\x58\x00\x10':
		return 0
	return 1

def noepyLoadRGBA(data, texList):
	bs = NoeBitStream(data)
	bs.seek(0x18, NOESEEK_ABS)
	imgWidth = bs.readUInt()
	imgHeight = bs.readUInt()
	bs.seek(0x4, NOESEEK_REL)
	imgFmt = bs.readUByte()
	bs.seek(0xB8, NOESEEK_ABS)
	offset = bs.readUInt()
	datasize = len(data) - offset
	bs.seek(offset, NOESEEK_ABS)
	data = bs.readBytes(datasize)
	#DXT1
	if imgFmt == 0x16 or imgFmt == 0x17:
		texFmt = noesis.NOESISTEX_DXT1
	#DXT5 packed normal map
	elif imgFmt == 0x1A:
		data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_ATI2)
		texFmt = noesis.NOESISTEX_RGBA32
		
	elif imgFmt == 0x18:
		data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_BC4)
		texFmt = noesis.NOESISTEX_RGBA32
		
	elif imgFmt == 0x1F or imgFmt == 0x1E:
		data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_BC7)
		texFmt = noesis.NOESISTEX_RGBA32

	#unknown, not handled
	else:
		print("WARNING: Unhandled image format " + repr(imgFmt) + " - " + repr(imgWidth) + "x" + repr(imgHeight) + " - " + repr(len(data)))
		return None
	texList.append(NoeTexture(rapi.getInputName(), imgWidth, imgHeight, data, texFmt))
	return 1