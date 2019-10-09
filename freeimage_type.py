from ctypes import c_uint8, c_int16, c_uint16, c_int32, c_uint32, c_float, c_double

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

def to_ctypes(fit, bpp):
    if fit == fit_unknown:
        logger.error("Could not specify the image type")
        raise Exception
    if fit == fit_bitmap:
        if bpp == 1:
            loggin.error("1-bit bitmap is not implemented")
            raise Exception
        elif bpp == 4:
            loggin.error("4-bit bitmap is not implemented")
            raise Exception
        elif bpp == 8:
            return c_uint8, 1
        elif bpp == 16:
            loggin.error("16-bit bitmap is not implemented")
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

def of_ctypes(c_type, count):
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

