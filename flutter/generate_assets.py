"""Generate app icon and splash screen PNGs using only Python stdlib.

Creates simple but professional-looking assets with a briefcase + magnifying glass motif.
Uses raw PNG encoding (zlib + struct) - no PIL/Pillow needed.
"""
import struct
import zlib
import os
import math

def create_png(width, height, pixels):
    """Create a PNG file from RGBA pixel data."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))

    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter none
        for x in range(width):
            idx = (y * width + x) * 4
            raw_data += bytes(pixels[idx:idx+4])

    idat = chunk(b'IDAT', zlib.compress(raw_data, 9))
    iend = chunk(b'IEND', b'')

    return header + ihdr + idat + iend


def blend(bg, fg, alpha):
    """Blend foreground onto background with alpha."""
    a = alpha / 255.0
    return int(bg * (1 - a) + fg * a)


def draw_circle(pixels, w, cx, cy, r, color, filled=True):
    """Draw a circle."""
    r2 = r * r
    for y in range(max(0, int(cy - r - 2)), min(int(cy + r + 2), len(pixels) // (w * 4))):
        for x in range(max(0, int(cx - r - 2)), min(int(cx + r + 2), w)):
            dx, dy = x - cx, y - cy
            dist2 = dx * dx + dy * dy
            if filled:
                if dist2 <= r2:
                    edge = max(0, min(255, int((r - math.sqrt(dist2)) * 255)))
                    edge = min(edge, 255)
                    idx = (y * w + x) * 4
                    pixels[idx] = blend(pixels[idx], color[0], min(edge, color[3]))
                    pixels[idx+1] = blend(pixels[idx+1], color[1], min(edge, color[3]))
                    pixels[idx+2] = blend(pixels[idx+2], color[2], min(edge, color[3]))
                    pixels[idx+3] = max(pixels[idx+3], min(edge, color[3]))
            else:
                dist = math.sqrt(dist2)
                thickness = r * 0.12
                if abs(dist - r) < thickness:
                    alpha = max(0, int((1 - abs(dist - r) / thickness) * 255))
                    alpha = min(alpha, color[3])
                    idx = (y * w + x) * 4
                    pixels[idx] = blend(pixels[idx], color[0], alpha)
                    pixels[idx+1] = blend(pixels[idx+1], color[1], alpha)
                    pixels[idx+2] = blend(pixels[idx+2], color[2], alpha)
                    pixels[idx+3] = max(pixels[idx+3], alpha)


def draw_rounded_rect(pixels, w, h, x1, y1, x2, y2, radius, color):
    """Draw a filled rounded rectangle."""
    for y in range(max(0, int(y1)), min(int(y2), h)):
        for x in range(max(0, int(x1)), min(int(x2), w)):
            inside = False
            # Check if inside rounded rect
            if x1 + radius <= x <= x2 - radius or y1 + radius <= y <= y2 - radius:
                inside = True
            else:
                # Check corners
                for cx, cy in [(x1+radius, y1+radius), (x2-radius, y1+radius),
                               (x1+radius, y2-radius), (x2-radius, y2-radius)]:
                    if (x - cx)**2 + (y - cy)**2 <= radius**2:
                        inside = True
                        break
            if inside:
                idx = (y * w + x) * 4
                pixels[idx] = blend(pixels[idx], color[0], color[3])
                pixels[idx+1] = blend(pixels[idx+1], color[1], color[3])
                pixels[idx+2] = blend(pixels[idx+2], color[2], color[3])
                pixels[idx+3] = max(pixels[idx+3], color[3])


def draw_line(pixels, w, h, x1, y1, x2, y2, thickness, color):
    """Draw a thick line."""
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    nx, ny = -dy/length, dx/length  # normal

    min_x = max(0, int(min(x1, x2) - thickness))
    max_x = min(w, int(max(x1, x2) + thickness))
    min_y = max(0, int(min(y1, y2) - thickness))
    max_y = min(h, int(max(y1, y2) + thickness))

    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            # Distance from point to line segment
            px, py = x - x1, y - y1
            t = max(0, min(1, (px*dx + py*dy) / (length*length)))
            proj_x, proj_y = x1 + t*dx - x, y1 + t*dy - y
            dist = math.sqrt(proj_x**2 + proj_y**2)
            if dist < thickness:
                alpha = max(0, int((1 - dist/thickness) * 255))
                alpha = min(alpha, color[3])
                idx = (y * w + x) * 4
                pixels[idx] = blend(pixels[idx], color[0], alpha)
                pixels[idx+1] = blend(pixels[idx+1], color[1], alpha)
                pixels[idx+2] = blend(pixels[idx+2], color[2], alpha)
                pixels[idx+3] = max(pixels[idx+3], alpha)


def create_app_icon(size=1024):
    """Create app icon: blue gradient background with white briefcase + magnifying glass."""
    pixels = [0] * (size * size * 4)

    # Blue gradient background
    for y in range(size):
        for x in range(size):
            t = y / size
            r = int(74 * (1-t) + 30 * t)    # #4A -> #1E
            g = int(144 * (1-t) + 80 * t)   # #90 -> #50
            b = int(226 * (1-t) + 160 * t)  # #E2 -> #A0
            idx = (y * size + x) * 4
            pixels[idx] = r
            pixels[idx+1] = g
            pixels[idx+2] = b
            pixels[idx+3] = 255

    white = (255, 255, 255, 240)
    cx, cy = size // 2, size // 2

    # Briefcase body
    bw, bh = int(size * 0.42), int(size * 0.30)
    bx1, by1 = cx - bw//2, cy - bh//2 + int(size*0.05)
    draw_rounded_rect(pixels, size, size, bx1, by1, bx1+bw, by1+bh, int(size*0.03), white)

    # Briefcase handle
    hw = int(size * 0.16)
    hh = int(size * 0.08)
    hx = cx - hw//2
    hy = by1 - hh + int(size*0.01)
    draw_rounded_rect(pixels, size, size, hx, hy, hx+hw, hy+hh, int(size*0.02), white)
    # Cut out handle interior
    inner_color = (int(74*0.7+30*0.3), int(144*0.7+80*0.3), int(226*0.7+160*0.3), 255)
    draw_rounded_rect(pixels, size, size, hx+int(size*0.025), hy+int(size*0.025),
                      hx+hw-int(size*0.025), by1+int(size*0.01), int(size*0.01), inner_color)

    # Briefcase center clasp
    clasp_w, clasp_h = int(size*0.06), int(size*0.04)
    clasp_color = (int(74*0.7+30*0.3), int(144*0.7+80*0.3), int(226*0.7+160*0.3), 255)
    draw_rounded_rect(pixels, size, size, cx-clasp_w//2, by1+bh//2-clasp_h//2,
                      cx+clasp_w//2, by1+bh//2+clasp_h//2, int(size*0.008), clasp_color)

    # Magnifying glass (bottom right)
    mg_cx = cx + int(size * 0.18)
    mg_cy = cy + int(size * 0.15)
    mg_r = int(size * 0.10)
    draw_circle(pixels, size, mg_cx, mg_cy, mg_r, white, filled=False)
    # Handle of magnifying glass
    angle = math.pi / 4
    hx1 = mg_cx + int(mg_r * math.cos(angle))
    hy1 = mg_cy + int(mg_r * math.sin(angle))
    hx2 = hx1 + int(size * 0.08)
    hy2 = hy1 + int(size * 0.08)
    draw_line(pixels, size, size, hx1, hy1, hx2, hy2, int(size*0.02), white)

    return pixels, size


def create_app_icon_foreground(size=1024):
    """Create foreground-only icon for adaptive icons (transparent bg)."""
    pixels = [0] * (size * size * 4)  # transparent

    white = (74, 144, 226, 255)  # Blue on transparent for foreground
    cx, cy = size // 2, size // 2

    # Briefcase body
    bw, bh = int(size * 0.35), int(size * 0.25)
    bx1, by1 = cx - bw//2, cy - bh//2 + int(size*0.03)
    draw_rounded_rect(pixels, size, size, bx1, by1, bx1+bw, by1+bh, int(size*0.025), white)

    # Briefcase handle
    hw = int(size * 0.14)
    hh = int(size * 0.07)
    hx = cx - hw//2
    hy = by1 - hh + int(size*0.01)
    draw_rounded_rect(pixels, size, size, hx, hy, hx+hw, hy+hh, int(size*0.015), white)
    # Cut out handle interior
    transparent = (0, 0, 0, 0)
    for y in range(int(hy+size*0.02), int(by1+size*0.005)):
        for x in range(int(hx+size*0.02), int(hx+hw-size*0.02)):
            idx = (y * size + x) * 4
            pixels[idx] = 0
            pixels[idx+1] = 0
            pixels[idx+2] = 0
            pixels[idx+3] = 0

    # Magnifying glass
    mg_cx = cx + int(size * 0.15)
    mg_cy = cy + int(size * 0.12)
    mg_r = int(size * 0.08)
    draw_circle(pixels, size, mg_cx, mg_cy, mg_r, white, filled=False)
    angle = math.pi / 4
    hx1 = mg_cx + int(mg_r * math.cos(angle))
    hy1 = mg_cy + int(mg_r * math.sin(angle))
    hx2 = hx1 + int(size * 0.07)
    hy2 = hy1 + int(size * 0.07)
    draw_line(pixels, size, size, hx1, hy1, hx2, hy2, int(size*0.018), white)

    return pixels, size


def create_splash_logo(size=512, dark=False):
    """Create splash logo (transparent background)."""
    pixels = [0] * (size * size * 4)

    color = (255, 255, 255, 255) if dark else (74, 144, 226, 255)
    cx, cy = size // 2, size // 2

    # Briefcase
    bw, bh = int(size * 0.45), int(size * 0.32)
    bx1, by1 = cx - bw//2, cy - bh//2 + int(size*0.03)
    draw_rounded_rect(pixels, size, size, bx1, by1, bx1+bw, by1+bh, int(size*0.03), color)

    # Handle
    hw = int(size * 0.18)
    hh = int(size * 0.09)
    hx = cx - hw//2
    hy = by1 - hh + int(size*0.01)
    draw_rounded_rect(pixels, size, size, hx, hy, hx+hw, hy+hh, int(size*0.02), color)
    for y in range(int(hy+size*0.025), int(by1+size*0.005)):
        for x in range(int(hx+size*0.025), int(hx+hw-size*0.025)):
            idx = (y * size + x) * 4
            pixels[idx] = pixels[idx+1] = pixels[idx+2] = pixels[idx+3] = 0

    # Magnifying glass
    mg_cx = cx + int(size * 0.20)
    mg_cy = cy + int(size * 0.16)
    mg_r = int(size * 0.10)
    draw_circle(pixels, size, mg_cx, mg_cy, mg_r, color, filled=False)
    angle = math.pi / 4
    hx1 = mg_cx + int(mg_r * math.cos(angle))
    hy1 = mg_cy + int(mg_r * math.sin(angle))
    draw_line(pixels, size, size, hx1, hy1,
              hx1 + int(size * 0.09), hy1 + int(size * 0.09),
              int(size*0.022), color)

    return pixels, size


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating app icon (1024x1024)...")
    pixels, size = create_app_icon(1024)
    png_data = create_png(size, size, pixels)
    path = os.path.join(script_dir, "assets", "icons", "app_icon.png")
    with open(path, 'wb') as f:
        f.write(png_data)
    print(f"  -> {path} ({len(png_data)} bytes)")

    print("Generating adaptive icon foreground (1024x1024)...")
    pixels, size = create_app_icon_foreground(1024)
    png_data = create_png(size, size, pixels)
    path = os.path.join(script_dir, "assets", "icons", "app_icon_foreground.png")
    with open(path, 'wb') as f:
        f.write(png_data)
    print(f"  -> {path} ({len(png_data)} bytes)")

    print("Generating splash logo (512x512)...")
    pixels, size = create_splash_logo(512, dark=False)
    png_data = create_png(size, size, pixels)
    path = os.path.join(script_dir, "assets", "splash", "splash_logo.png")
    with open(path, 'wb') as f:
        f.write(png_data)
    print(f"  -> {path} ({len(png_data)} bytes)")

    print("Generating dark splash logo (512x512)...")
    pixels, size = create_splash_logo(512, dark=True)
    png_data = create_png(size, size, pixels)
    path = os.path.join(script_dir, "assets", "splash", "splash_logo_dark.png")
    with open(path, 'wb') as f:
        f.write(png_data)
    print(f"  -> {path} ({len(png_data)} bytes)")

    print("\nAll assets generated!")
    print("Next: flutter pub run flutter_launcher_icons")
    print("Next: flutter pub run flutter_native_splash:create")


if __name__ == "__main__":
    main()
