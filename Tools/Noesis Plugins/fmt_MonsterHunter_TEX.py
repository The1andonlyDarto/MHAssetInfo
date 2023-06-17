#Monster Hunter 3 Ultimate .TEX [Wii U] - ".TEX" Loader
#By Zaramot
#v1.0
#Special thanks: Chrrox

from inc_noesis import *
import subprocess

def registerNoesisTypes():
	handle = noesis.register("Monster Hunter 3 Ultimate Texture [Wii U]", ".tex")
	noesis.setHandlerTypeCheck(handle, texCheckType)
	noesis.setHandlerLoadRGBA(handle, texLoadDDS)
	noesis.logPopup()
	return 1
		
def texCheckType(data):
	bs = NoeBitStream(data, NOE_BIGENDIAN)
	fileMagic = bs.readUInt()
	if fileMagic == 0x584554:
		return 1
	else: 
		print("Fatal Error: Unknown file magic: " + str(hex(fileMagic) + " expected 0x584554!"))
		return 0

def texLoadDDS(data, texList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
	
    fileMagic = bs.readUInt()
    bs.seek(0x8, NOESEEK_ABS) #Entry start
    ddsName = rapi.getLocalFileName(rapi.getInputName())
    print (ddsName)
    TWidth = bs.readUByte()
    if TWidth == 0x31:
	    Width = 2048 
    elif TWidth == 0x2C: 
	    Width = 1024 
    elif TWidth == 0x28: 
	    Width = 512 
    elif TWidth == 0x24: 
	    Width = 256 
    elif TWidth == 0x20:  
	    Width = 128  
    elif TWidth == 0x5: 
        Width = 2048
    else: 
	    print("WARNING: Unhandled image format " + repr(Width) + "x" + repr(Height))
    Unk = bs.readUByte()
    Height = bs.readUShort()
    print (Width)
    print (Height)

    gtxTex = (b'\x47\x66\x78\x32\x00\x00\x00\x20\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0A\x00\x00\x00\x9C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')
    gtxWidth = struct.pack(">I", Width)
    gtxheight = struct.pack(">I", Height)
    gtxTex += gtxWidth
    gtxTex += gtxheight
    gtxTex += (b'\x00\x00\x00\x01\x00\x00\x00\x01')
    bs.seek(0xC, NOESEEK_ABS)	
    TexInd = bs.readUShort()     
    print (TexInd)
    bs.seek(0x10, NOESEEK_ABS) #DDS
    if TexInd == 268:
	    ddsFmt = noesis.NOESISTEX_DXT3
	    type = struct.pack(">I", 50)
	    gtxFmt =  struct.pack(">I", 0xCC0003FF)
	    pixelInfo = struct.pack(">II", 8192, 256)
	    ddsSize = (Width * Height * 8) // 8
		
	    ddsData = bs.readBytes(ddsSize)
		
    elif TexInd == 267:
	    ddsFmt = noesis.NOESISTEX_DXT1
	    type = struct.pack(">I", 49)
	    gtxFmt =  struct.pack(">I", 0xC40003FF)
	    pixelInfo = struct.pack(">II", 4096, 256)
	    ddsSize = (Width * Height * 4) // 8
		
	    ddsData = bs.readBytes(ddsSize)  
    
    print (ddsFmt)
	
    gtxTex += type
    gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x01')
    gtxTex += struct.pack(">I", ddsSize)
    gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x0D\x00\x00')
    gtxTex += pixelInfo
    gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x02\x03\x1F\xF8\x7F\x21')
    gtxTex += gtxFmt
    gtxTex += (b'\x06\x88\x84\x00\x00\x00\x00\x00\x80\x00\x00\x10\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0B')
    gtxTex += struct.pack(">I", ddsSize)
    gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x00')
    gtxTex += ddsData
    gtxTex += (b'\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    dstFilePath = noesis.getScenesPath() + ddsName + ".gtx"
    workingdir = noesis.getScenesPath()
    newfile = open(dstFilePath,'wb')
    newfile.write(gtxTex)
    newfile.close()
    subprocess.Popen([noesis.getScenesPath() + 'TexConv2.bat', dstFilePath]).wait()
    try:
            texData = rapi.loadIntoByteArray(dstFilePath + ".dds")
            texture = rapi.loadTexByHandler(texData, ".dds")
    except:
	    texture = NoeTexture(str(len(self.texList)), 0, 0, None, noesis.NOESISTEX_RGBA32)
    texture.name = ddsName
    texList.append(texture)
    #tex1 = NoeTexture(ddsName, Width, Height, ddsData, ddsFmt)
    #texList.append(tex1)

    return 1
	