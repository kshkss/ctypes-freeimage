import os
import logging
from ctypes import *
import numpy as np
import numpy.ctypeslib as npct
from . import freeimage_type as FIT
from . import freeimage_format as FIF

logger = logging.getLogger(__name__)

if os.name == 'posix':
    libcd = cdll.LoadLibrary("libfreeimage.so")
elif os.name == 'nt':
    libcd = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "FreeImage.dll"))
else:
    logger.error("Unsupported OS.")
    raise Exception

fib_p = POINTER(c_void_p)
fitype = c_int
fiformat = c_int

libcd.FreeImage_Initialise.restype = None
libcd.FreeImage_Initialise.argtype = None

libcd.FreeImage_GetFileType.restype = fiformat
libcd.FreeImage_GetFileType.argtype = [c_char_p, c_int]

libcd.FreeImage_GetFIFFromFilename.restype = fiformat
libcd.FreeImage_GetFIFFromFilename.argtype = [c_char_p]

libcd.FreeImage_AllocateT.restype = fib_p
libcd.FreeImage_AllocateT.argtype = [fitype, c_int, c_int, c_int]

libcd.FreeImage_Load.restype = fib_p
libcd.FreeImage_Load.argtype = [fiformat, c_char_p, c_int]

libcd.FreeImage_Save.restype = c_bool
libcd.FreeImage_Save.argtype = [fiformat, fib_p, c_char_p, c_int]

libcd.FreeImage_Unload.restype = None
libcd.FreeImage_Unload.argtype = [fib_p]

libcd.FreeImage_GetImageType.restype = fitype
libcd.FreeImage_GetImageType.argtype = [fib_p]

libcd.FreeImage_GetWidth.restype = c_uint
libcd.FreeImage_GetWidth.argtype = [fib_p]

libcd.FreeImage_GetHeight.restype = c_uint
libcd.FreeImage_GetHeight.argtype = [fib_p]

libcd.FreeImage_GetHeight.restype = c_uint
libcd.FreeImage_GetHeight.argtype = [fib_p]

libcd.FreeImage_GetPitch.restype = c_uint
libcd.FreeImage_GetPitch.argtype = [fib_p]

libcd.FreeImage_GetBPP.restype = c_uint
libcd.FreeImage_GetBPP.argtype = [fib_p]

#libcd.FreeImage_GetBits.restype = c_void_p
#libcd.FreeImage_GetBits.argtype = [fib_p]

libcd.FreeImage_GetScanLine.restype = POINTER(None)
libcd.FreeImage_GetScanLine.argtype = [fib_p, c_int]

libcd.FreeImage_EnlargeCanvas.restype = fib_p
libcd.FreeImage_EnlargeCanvas.argtype = [fib_p, c_int, c_int, c_int, c_int, POINTER(None), c_int]

def image_info(image):
    if(image.ndim == 2):
        height, width = image.shape
        return (width, height, 1, image[0:1, 0:1].nbytes * 8)
    elif(image.ndim == 3):
        height, width, count = image.shape
        return (width, height, count, image[0:1, 0:1, 0:1].nbytes * 8)

class FIBitmap:
    rawptr = POINTER(c_void_p)
    width = 0
    height = 0
    ctype = c_int
    samples = 0

    def __init__(self, ptr, *, width=None, height=None, ctype=None, samples=None):
        self.rawptr = ptr
        if width is None:
            self.width = libcd.FreeImage_GetWidth(ptr)
        else:
            self.width = width
        if height is None:
            self.height = libcd.FreeImage_GetHeight(ptr)
        else:
            self.height = height
        if ctype is None or samples is None:
            fit = libcd.FreeImage_GetImageType(self.rawptr)
            bpp = libcd.FreeImage_GetBPP(self.rawptr)
            c_type, sample_count = FIT.to_ctypes(fit, bpp)
            self.ctype = c_type
            self.samples = sample_count
        else:
            self.ctype = ctype
            self.samples = samples

    def unload(self):
        libcd.FreeImage_Unload(self.rawptr)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.unload()
        return False

    def to_ndarray(self):
        width = self.width
        height = self.height
        c_type = self.ctype
        sample_count = self.samples
        lines = [npct.as_array( cast(libcd.FreeImage_GetScanLine(self.rawptr, int(i)), POINTER(c_type)), shape=(width*sample_count,) ) for i in range(0, height)]
        lines.reverse()
        image = np.stack(lines)
        if sample_count == 1:
            return image
        else:
            return image.reshape(height, width, sample_count)

    def save(self, filename, *, option=0):
        c_filename = filename.encode('utf-8')
        fif = libcd.FreeImage_GetFIFFromFilename(c_filename)
        if fif == FIF.unknown:
            logger.error("Could not specify the image format of '{}'".format(filename))
            raise Exception
        libcd.FreeImage_Save(fif, self.rawptr, c_filename, option)

    def move(self, dx, dy, *, background=[0,0,0,0]):
        src = self.rawptr
        color_type = self.ctype * self.samples
        color = color_type()
        for i in range(self.samples):
            color[i] = background[i]
        res = libcd.FreeImage_EnlargeCanvas(src, dx, dy, -dx, -dy, color, 0)
        if not bool(res):
            logger.error("Failed to create an enlarged image.")
            raise Exception
        return FIBitmap(res)

def load(filename):
    c_filename = filename.encode('utf-8')
    fif = libcd.FreeImage_GetFileType(c_filename, 0)
    if fif == FIF.unknown:
        logger.warn("Could not specify the image format of {} by `GetFileType'".format(filename))
        fif = libcd.FreeImage_GetFIFFromFilename(c_filename)
    if fif == FIF.unknown:
        logger.error("Could not specify the image format of {}".format(filename))
        raise Exception
    ptr = libcd.FreeImage_Load(fif, c_filename, 0)
    if not bool(ptr):
        logger.error("Failed to load the image: {}".format(filename))
        raise Exception
    return FIBitmap(ptr)

def from_ndarray(image):
    if not (image.ndim == 2 or image.ndim == 3):
        logger.error("{}-dimensional array is unsupported".format(image.ndim))
        raise Exception
    width, height, count, bps = image_info(image)
    c_type = npct.as_ctypes_type(image.dtype)
    image = image.reshape(height, count*width)
    ptr = libcd.FreeImage_AllocateT(FIT.of_ctypes(c_type, count), width, height, count*bps)
    if not bool(ptr):
        logger.error("Failed to allocate an image whose size is {}x{}x{}", width, height, count)
        raise Exception
    for i in range(0, height):
        out = npct.as_array( cast(libcd.FreeImage_GetScanLine(ptr, int(i)), POINTER(c_type)), shape=(width*count,) )
        np.copyto(out, image[height - 1 - i])
    return FIBitmap(ptr, width=width, height=height, ctype=c_type, channels=count)
 
def imread(filename):
    with load(filename) as fib:
        return fib.to_ndarray()

def imwrite(filename, image, *, option=0):
    with from_ndarray(image) as fib:
        fib.save(filename, option=option)

