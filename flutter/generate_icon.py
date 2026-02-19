"""Fast app icon generator using arrays. Creates a clean blue gradient with 'JS' text-like motif."""
import struct, zlib, array, math, os

def make_png(w, h, buf):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        off = y * w * 4
        raw.extend(buf[off:off + w * 4])
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')

def gen_icon(size):
    buf = bytearray(size * size * 4)
    # Blue gradient background
    for y in range(size):
        t = y / size
        r, g, b = int(60*(1-t)+20*t), int(130*(1-t)+70*t), int(220*(1-t)+150*t)
        for x in range(size):
            o = (y * size + x) * 4
            buf[o], buf[o+1], buf[o+2], buf[o+3] = r, g, b, 255

    # Draw white briefcase shape
    cx, cy = size//2, size//2 + size//20
    bw, bh = size*42//100, size*28//100
    r = size*3//100
    _draw_rrect(buf, size, cx-bw//2, cy-bh//2, bw, bh, r, 255, 255, 255)

    # Handle
    hw, hh = size*15//100, size*8//100
    hy = cy - bh//2 - hh + size//80
    _draw_rrect(buf, size, cx-hw//2, hy, hw, hh, r, 255, 255, 255)
    # Inner cutout of handle
    ihm, ivm = size*25//1000, size*2//100
    _draw_rrect(buf, size, cx-hw//2+ihm, hy+ivm, hw-ihm*2, hh-ivm+size//80, r//2, 50, 110, 195)

    # Magnifying glass circle (bottom-right)
    mgx, mgy = cx + size*17//100, cy + size*12//100
    mgr = size*9//100
    _draw_ring(buf, size, mgx, mgy, mgr, size*12//1000, 255, 255, 255)
    # Handle
    ang = math.pi/4
    lx1 = mgx + int(mgr * math.cos(ang))
    ly1 = mgy + int(mgr * math.sin(ang))
    lx2 = lx1 + size*7//100
    ly2 = ly1 + size*7//100
    _draw_thick_line(buf, size, lx1, ly1, lx2, ly2, size*2//100, 255, 255, 255)

    return buf

def gen_foreground(size):
    buf = bytearray(size * size * 4)  # transparent
    cr, cg, cb = 60, 130, 220
    cx, cy = size//2, size//2 + size//20
    bw, bh = size*35//100, size*23//100
    r = size*25//1000
    _draw_rrect(buf, size, cx-bw//2, cy-bh//2, bw, bh, r, cr, cg, cb)
    hw, hh = size*13//100, size*7//100
    hy = cy - bh//2 - hh + size//80
    _draw_rrect(buf, size, cx-hw//2, hy, hw, hh, r, cr, cg, cb)
    ihm, ivm = size*2//100, size*18//1000
    _draw_rrect(buf, size, cx-hw//2+ihm, hy+ivm, hw-ihm*2, hh-ivm+size//80, r//2, 0, 0, 0, alpha=0)
    mgx, mgy = cx + size*15//100, cy + size*10//100
    mgr = size*7//100
    _draw_ring(buf, size, mgx, mgy, mgr, size//100, cr, cg, cb)
    ang = math.pi/4
    lx1 = mgx + int(mgr * math.cos(ang))
    ly1 = mgy + int(mgr * math.sin(ang))
    _draw_thick_line(buf, size, lx1, ly1, lx1+size*6//100, ly1+size*6//100, size*15//1000, cr, cg, cb)
    return buf

def gen_splash(size, dark=False):
    buf = bytearray(size * size * 4)
    cr, cg, cb = (255,255,255) if dark else (60,130,220)
    cx, cy = size//2, size//2
    bw, bh = size*40//100, size*28//100
    r = size*3//100
    _draw_rrect(buf, size, cx-bw//2, cy-bh//2, bw, bh, r, cr, cg, cb)
    hw, hh = size*16//100, size*8//100
    hy = cy - bh//2 - hh + size//60
    _draw_rrect(buf, size, cx-hw//2, hy, hw, hh, r, cr, cg, cb)
    ihm, ivm = size*22//1000, size*2//100
    _draw_rrect(buf, size, cx-hw//2+ihm, hy+ivm, hw-ihm*2, hh-ivm+size//60, r//2, 0, 0, 0, alpha=0)
    mgx, mgy = cx + size*18//100, cy + size*14//100
    mgr = size*9//100
    _draw_ring(buf, size, mgx, mgy, mgr, size*12//1000, cr, cg, cb)
    ang = math.pi/4
    lx1 = mgx + int(mgr * math.cos(ang))
    ly1 = mgy + int(mgr * math.sin(ang))
    _draw_thick_line(buf, size, lx1, ly1, lx1+size*8//100, ly1+size*8//100, size*2//100, cr, cg, cb)
    return buf

def _draw_rrect(buf, sz, x, y, w, h, rad, r, g, b, alpha=255):
    for py in range(max(0,y), min(sz, y+h)):
        for px in range(max(0,x), min(sz, x+w)):
            inside = False
            if x+rad <= px <= x+w-rad or y+rad <= py <= y+h-rad:
                inside = True
            else:
                for ccx, ccy in [(x+rad,y+rad),(x+w-rad,y+rad),(x+rad,y+h-rad),(x+w-rad,y+h-rad)]:
                    if (px-ccx)**2+(py-ccy)**2 <= rad**2:
                        inside = True
                        break
            if inside:
                o = (py*sz+px)*4
                buf[o], buf[o+1], buf[o+2], buf[o+3] = r, g, b, alpha

def _draw_ring(buf, sz, cx, cy, rad, thick, r, g, b):
    for py in range(max(0, cy-rad-thick-1), min(sz, cy+rad+thick+2)):
        for px in range(max(0, cx-rad-thick-1), min(sz, cx+rad+thick+2)):
            d = math.sqrt((px-cx)**2+(py-cy)**2)
            if abs(d - rad) <= thick:
                o = (py*sz+px)*4
                buf[o], buf[o+1], buf[o+2], buf[o+3] = r, g, b, 255

def _draw_thick_line(buf, sz, x1, y1, x2, y2, thick, r, g, b):
    dx, dy = x2-x1, y2-y1
    ln = math.sqrt(dx*dx+dy*dy)
    if ln == 0: return
    for py in range(max(0, min(y1,y2)-thick), min(sz, max(y1,y2)+thick)):
        for px in range(max(0, min(x1,x2)-thick), min(sz, max(x1,x2)+thick)):
            t = max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/(ln*ln)))
            dist = math.sqrt((x1+t*dx-px)**2+(y1+t*dy-py)**2)
            if dist < thick:
                o = (py*sz+px)*4
                buf[o], buf[o+1], buf[o+2], buf[o+3] = r, g, b, 255

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    for name, func, sz in [
        ('assets/icons/app_icon.png', gen_icon, 512),
        ('assets/icons/app_icon_foreground.png', gen_foreground, 512),
        ('assets/splash/splash_logo.png', lambda s: gen_splash(s, False), 384),
        ('assets/splash/splash_logo_dark.png', lambda s: gen_splash(s, True), 384),
    ]:
        print(f'Generating {name} ({sz}x{sz})...')
        buf = func(sz)
        data = make_png(sz, sz, buf)
        path = os.path.join(base, name.replace('/', os.sep))
        with open(path, 'wb') as f:
            f.write(data)
        print(f'  -> {len(data)} bytes')
    print('Done!')
