import os
import logging
from ctypes import *
import numpy as np
import numpy.ctypeslib as npct

logger = logging.getLogger()

libcd = cdll.LoadLibrary("libfreeimage.so")

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

fif_unknown = -1
fif_tiff = 18

fit_unknown = 0
fit_bitmap = 1   # standard image		: 1-, 4-, 8-, 16-, 24-, 32-bit
fit_uint16 = 2
fit_int16 = 3
fit_uint32 = 4
fit_int32 = 5
fit_float = 6
fit_double = 7
fit_complex = 8  # array of FICOMPLEX		: 2 x 64-bit IEEE floating point
fit_rgb16 = 9    # 48-bit RGB image		: 3 x 16-bit
fit_rgba16 = 10  # 64-bit RGBA image		: 4 x 16-bit
fit_rgbf = 11    # 96-bit RGB float image	: 3 x 32-bit IEEE floating point
fit_rgbaf = 12   # 128-bit RGBA float image	: 4 x 32-bit IEEE floating point

# Load/Save flags for tiff format
tiff_default = 0
tiff_packbits = 0x0100         # save using PACKBITS compression
tiff_deflate = 0x0200          # save using DEFLATE compression (a.k.a. ZLIB compression)
tiff_adobe_deflate = 0x0400
tiff_none = 0x0800             # save without any compression
tiff_lzw = 0x4000              # save using LZW compression
tiff_jpeg = 0x8000             # save using JPEG compression
tiff_logluv = 0x10000          # save using LogLuv compression

def of_free_image_type(fib, filename):
    fit = libcd.FreeImage_GetImageType(fib)
    if fit == fit_unknown:
        logger.error("Could not specify the image type of {}".format(filename))
        raise Exception
    if fit == fit_bitmap:
        bpp = libcd.FreeImage_GetBPP(fib)
        if bpp == 1:
            loggin.error("1-bit bitmap is not implemented: {}".format(filename))
            raise Exception
        elif bpp == 4:
            loggin.error("4-bit bitmap is not implemented: {}".format(filename))
            raise Exception
        elif bpp == 8:
            return c_uint8, 1
        elif bpp == 16:
            loggin.error("16-bit bitmap is not implemented: {}".format(filename))
            raise Exception
        elif bpp == 24:
            return c_uint8, 3
        elif bpp == 32:
            return c_uint8, 4
        else:
            loggin.error("This library has some problems")
            raise Exception
    elif fit == fit_int16:
        return c_int16, 1
    elif fit == fit_uint16:
        return c_uint16, 1
    elif fit == fit_int32:
        return c_int32, 1
    elif fit == fit_uint32:
        return c_uint32, 1
    elif fit == fit_float:
        return c_float, 1
    elif fit == fit_double:
        return c_double, 1
    elif fit == fit_complex:
        return c_double, 2
    elif fit == fit_rgb16:
        return c_uint16, 3
    elif fit == fit_rgba16:
        return c_uint16, 4
    elif fit == fit_rgbf:
        return c_double, 3
    elif fit == fit_rgbaf:
        return c_double, 4
    else:
        logging.error("This library has some problems")
        raise Exception

def to_free_image_type(c_type, count):
    if c_type == c_uint8 or c_type == np.uint8:
        return fit_bitmap
    elif c_type == c_int16 or c_type == np.int16:
        if count == 1:
            return fit_int16
        else:
            0 # go to the last of this function
    elif c_type == c_uint16 or c_type == np.uint16:
        if count == 1:
            return fit_uint16
        elif count == 3:
            return fit_rgb16
        elif count == 4:
            return fit_rgba16
        else:
            0 # go to the last of this function
    elif c_type == c_int32 or c_type == np.int32:
        if count == 1:
            return fit_int16
        else:
            0 # go to the last of this function
    elif c_type == c_uint32 or c_type == np.uint32:
        if count == 1:
            return fit_uint32
        else:
            0 # go to the last of this function
    elif c_type == c_float or c_type == np.float32:
        if count == 1:
            return fit_float
        else:
            0 # go to the last of this function
    elif c_type == c_double or c_type == np.float64:
        if count == 1:
            return fit_double
        elif count == 2:
            return fit_complex
        elif count == 3:
            return fit_rgbf
        elif count == 4:
            return fit_rgbaf
        else:
            0 # go to the last of this function
    else:
        logging.error("Unsupported element type: {}".format(c_type))
        raise Exception
    logging.error("Unsupported sample number per pixcel: elsement type = {}, num. of samples = {}".format(c_type, count))
    raise Exception


def imread(filename):
    c_filename = filename.encode('utf-8')
    fif = libcd.FreeImage_GetFileType(c_filename, 0)
    if fif == fif_unknown:
        logger.warn("Could not specify the image format of {} by `GetFileType'".format(filename))
        fif = libcd.FreeImage_GetFIFFromFilename(c_filename)
    if fif == fif_unknown:
        logger.error("Could not specify the image format of {}".format(filename))
        raise Exception
    fib = libcd.FreeImage_Load(fif, c_filename, 0)
    if not bool(fib):
        logger.error("Failed to load the image: {}".format(filename))
        raise Exception
    width = libcd.FreeImage_GetWidth(fib)
    height = libcd.FreeImage_GetHeight(fib)
    c_type, sample_count = of_free_image_type(fib, filename)
    lines = [npct.as_array( cast(libcd.FreeImage_GetScanLine(fib, int(i)), POINTER(c_type)), shape=(width*sample_count,) ) for i in range(0, height)]
    lines.reverse()
    image = np.stack(lines)
    libcd.FreeImage_Unload(fib)
    if sample_count == 1:
        return image
    else:
        return image.reshape(height, width, sample_count)

def image_info(image):
    if(image.ndim == 2):
        height, width = image.shape
        return (width, height, 1, image[0:1, 0:1].nbytes * 8)
    elif(image.ndim == 3):
        height, width, count = image.shape
        return (width, height, count, image[0:1, 0:1, 0:1].nbytes * 8)

def imwrite(filename, image, *, compress=None):
    c_filename = filename.encode('utf-8')
    if not (image.ndim == 2 or image.ndim == 3):
        logger.error("{}-dimensional array is unsupported".format(image.ndim))
        raise Exception
    fif = libcd.FreeImage_GetFIFFromFilename(c_filename)
    if fif == fif_unknown:
        logger.error("Could not specify the image format of '{}'".format(filename))
        raise Exception
    width, height, count, bps = image_info(image)
    c_type = npct.as_ctypes_type(image.dtype)
    image = image.reshape(height, count*width)
    fib = libcd.FreeImage_AllocateT(to_free_image_type(c_type, count), width, height, count*bps)
    if not bool(fib):
        logger.error("Failed to allocate an image whose size is {}x{}x{}", width, height, count)
        raise Exception
    for i in range(0, height):
        out = npct.as_array( cast(libcd.FreeImage_GetScanLine(fib, int(i)), POINTER(c_type)), shape=(width*count,) )
        np.copyto(out, image[height - 1 - i])
    if compress == None:
        libcd.FreeImage_Save(fif, fib, c_filename, 0)
    elif fif == fif_tiff:
        if compress == "zip" or compress == "ZIP" or compress == "ztsd" or compress == "ZSTD" or compress == "LZ77" or compress == "lz77" or compress == "DEFLATE" or compress == "deflate":
            libcd.FreeImage_Save(fif, fib, c_filename, tiff_deflate)
        elif compress == "adobe_deflate" or compress == "ADOBE_DEFLATE":
            libcd.FreeImage_Save(fif, fib, c_filename, tiff_adobe_deflate)
        elif compress == "lzw" or compress == "LZW":
            libcd.FreeImage_Save(fif, fib, c_filename, tiff_lzw)
        elif compress == "jpeg" or compress == "JPEG":
            libcd.FreeImage_Save(fif, fib, c_filename, tiff_jpeg)
        elif compress == "logluv" or compress == "LOGLUV":
            libcd.FreeImage_Save(fif, fib, c_filename, tiff_logluv)
        elif compress == "none" or compress == "None":
            libcd.FreeImage_Save(fif, fib, c_filename, tiff_none)
        else:
            logger.error("unsupported compression: '{}'".format(compress))
            raise Exception
    else:
        logger.error("Compression option in `imwrite' is supported only for tiff")
        raise Exception
    libcd.FreeImage_Unload(fib)

