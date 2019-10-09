# Load/Save flags for tiff format
default = 0
packbits = 0x0100         # save using PACKBITS compression
deflate = 0x0200          # save using DEFLATE compression (a.k.a. ZLIB compression)
adobe_deflate = 0x0400
none = 0x0800             # save without any compression
lzw = 0x4000              # save using LZW compression
jpeg = 0x8000             # save using JPEG compression
logluv = 0x10000          # save using LogLuv compression

