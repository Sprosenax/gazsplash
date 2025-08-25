#!/usr/bin/env python3
import struct, sys, glob, os
from PIL import Image

# ---------------- RLE24 CODEC ---------------- #

def decode_rle24_bgr(block, width, height):
    pixels = []
    i = 0
    while i < len(block) and len(pixels) < width * height:
        control = block[i]; i += 1
        if control & 0x80:  # run
            if i + 3 > len(block): break
            b, g, r = block[i], block[i+1], block[i+2]; i += 3
            run_len = (control & 0x7F) + 1
            pixels.extend([(r, g, b)] * run_len)
        else:  # literal
            run_len = (control & 0x7F) + 1
            for _ in range(run_len):
                if i + 3 > len(block): break
                b, g, r = block[i], block[i+1], block[i+2]; i += 3
                pixels.append((r, g, b))
    pixels = pixels[:width*height]
    if len(pixels) < width*height:
        pixels.extend([(0,0,0)] * (width*height - len(pixels)))
    return pixels

def encode_rle24_bgr(pixels):
    out = bytearray(); i, n = 0, len(pixels)
    while i < n:
        # Run
        run_len = 1
        while i + run_len < n and pixels[i+run_len] == pixels[i] and run_len < 128:
            run_len += 1
        if run_len > 1:
            out.append(0x80 | (run_len - 1))
            r,g,b = pixels[i]; out.extend([b,g,r]); i += run_len; continue
        # Literal
        start = i; i += 1
        while i < n and (pixels[i] != pixels[i-1] or i-start == 1) and (i-start) < 128:
            i += 1
        lit_len = i - start
        out.append(lit_len - 1)
        for j in range(start, i):
            r,g,b = pixels[j]; out.extend([b,g,r])
    return bytes(out)

# ---------------- FILE IO ---------------- #

def save_bmp(pixels, width, height, out_file):
    row_padded = (width * 3 + 3) & ~3
    img_size = row_padded * height
    filesize = 54 + img_size
    with open(out_file, "wb") as f:
        f.write(b'BM')
        f.write(struct.pack("<I", filesize))
        f.write(b'\x00\x00'); f.write(b'\x00\x00')
        f.write(struct.pack("<I", 54))
        f.write(struct.pack("<I", 40))
        f.write(struct.pack("<i", width))
        f.write(struct.pack("<i", height))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", 24))
        f.write(struct.pack("<I", 0))
        f.write(struct.pack("<I", img_size))
        f.write(struct.pack("<i", 0)); f.write(struct.pack("<i", 0))
        f.write(struct.pack("<I", 0)); f.write(struct.pack("<I", 0))
        for y in range(height-1, -1, -1):
            row = b''.join(struct.pack("BBB", p[2], p[1], p[0]) for p in pixels[y*width:(y+1)*width])
            f.write(row)
            f.write(b'\x00' * (row_padded - width*3))

def load_bmp_pixels(bmp_path, expect_w=None, expect_h=None):
    img = Image.open(bmp_path).convert("RGB")
    w,h = img.size
    if expect_w and expect_h and (w != expect_w or h != expect_h):
        raise ValueError(f"{bmp_path}: must be {expect_w}x{expect_h}, got {w}x{h}")
    return list(img.getdata()), w, h

# ---------------- SPLASH FORMAT ---------------- #

def unpack_splash(filename):
    data = open(filename, "rb").read()
    filesize = len(data); idx = 0
    for pos in range(0, filesize-32):
        if data[pos:pos+8] == b"SPLASH!!":
            width  = struct.unpack_from("<I", data, pos+8)[0]
            height = struct.unpack_from("<I", data, pos+12)[0]
            fmt    = struct.unpack_from("<I", data, pos+16)[0]
            sectors= struct.unpack_from("<I", data, pos+20)[0]
            size   = sectors * 512
            payload_off = pos + 0x100 + 256
            block = data[payload_off:payload_off+size-256]
            pixels = decode_rle24_bgr(block, width, height)
            out_bmp = f"index{idx}.bmp"
            save_bmp(pixels, width, height, out_bmp)
            print(f"✅ Extracted {out_bmp} ({width}x{height})")
            idx += 1
    if idx == 0: print("❌ No splash headers found")

def build_entry(pixels, width, height):
    encoded = encode_rle24_bgr(pixels)
    encoded = b'\x00'*256 + encoded
    sectors = (len(encoded) + 511)//512
    header = b"SPLASH!!" + struct.pack("<I", width) + struct.pack("<I", height)
    header += struct.pack("<I", 1) + struct.pack("<I", sectors)
    header += b'\x00'*(0x100-len(header))
    payload = encoded + b'\x00'*(sectors*512 - len(encoded))
    return header + payload

def pack_splash(out_file):
    bmp_files = sorted(glob.glob("index*.bmp"))
    if not bmp_files:
        print("❌ No indexN.bmp files found in current folder")
        return

    # Ensure sequential indexes (no gaps)
    expected = [f"index{i}.bmp" for i in range(len(bmp_files))]
    if bmp_files != expected:
        print(f"❌ Missing or misnumbered BMPs. Found: {bmp_files}, expected: {expected}")
        return

    out = b""; expected_size = None
    for bmp in bmp_files:
        pixels,w,h = load_bmp_pixels(bmp, *expected_size) if expected_size else load_bmp_pixels(bmp)
        if expected_size is None:
            expected_size = (w,h)
        out += build_entry(pixels,w,h)

    with open(out_file,"wb") as f: f.write(out)
    print(f"✅ Built {out_file} with {len(bmp_files)} entries ({expected_size[0]}x{expected_size[1]})")

# ---------------- CLI ---------------- #

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  splashtool.py unpack splash.img")
        print("  splashtool.py pack splash_new.img")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "unpack":
        unpack_splash(sys.argv[2])
    elif cmd == "pack":
        pack_splash(sys.argv[2])
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
