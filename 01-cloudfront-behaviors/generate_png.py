import zlib
import struct
import os

def create_png_rgba(width, height, get_pixel_func):
    """
    Pure Python PNG generator using standard library zlib.
    """
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter type 0 (None)
        for x in range(width):
            r, g, b, a = get_pixel_func(x, y, width, height)
            raw_data.extend([r, g, b, a])
            
    compressed = zlib.compress(bytes(raw_data), 9)
    
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    
    # IHDR
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png.extend(struct.pack(">I", len(ihdr)))
    png.extend(b'IHDR')
    png.extend(ihdr)
    png.extend(struct.pack(">I", zlib.crc32(b'IHDR' + ihdr)))
    
    # IDAT
    png.extend(struct.pack(">I", len(compressed)))
    png.extend(b'IDAT')
    png.extend(compressed)
    png.extend(struct.pack(">I", zlib.crc32(b'IDAT' + compressed)))
    
    # IEND
    png.extend(struct.pack(">I", 0))
    png.extend(b'IEND')
    png.extend(struct.pack(">I", zlib.crc32(b'IEND')))
    
    return bytes(png)

def generate_architecture_png(output_path):
    width, height = 1200, 700
    
    # Simple rasterizer for clean architecture diagram image
    # Background: #FFFFFF with subtle light gray border
    canvas = [[(255, 255, 255, 255) for _ in range(width)] for _ in range(height)]
    
    def fill_rect(x1, y1, w, h, color, border_color=None, border_w=1):
        for y in range(max(0, y1), min(height, y1 + h)):
            for x in range(max(0, x1), min(width, x1 + w)):
                is_border = (border_color is not None) and (
                    x < x1 + border_w or x >= x1 + w - border_w or
                    y < y1 + border_w or y >= y1 + h - border_w
                )
                canvas[y][x] = border_color if is_border else color

    # Draw grid
    for y in range(0, height, 40):
        for x in range(0, width, 40):
            canvas[y][x] = (240, 243, 246, 255)

    # Box 1: User / Browser (Top Left)
    fill_rect(80, 280, 200, 140, (248, 250, 252, 255), (203, 213, 225, 255), 2)
    # Box 2: CloudFront (Center)
    fill_rect(380, 180, 280, 340, (255, 251, 235, 255), (255, 153, 0, 255), 3)
    # Box 3: S3 Assets (Top Right)
    fill_rect(780, 80, 340, 140, (240, 253, 244, 255), (34, 197, 94, 255), 2)
    # Box 4: ALB Backend (Middle Right)
    fill_rect(780, 280, 340, 140, (254, 242, 242, 255), (239, 68, 68, 255), 2)
    # Box 5: S3 SPA (Bottom Right)
    fill_rect(780, 480, 340, 140, (239, 246, 255, 255), (59, 130, 246, 255), 2)

    # Connecting lines / Arrows (horizontal bands)
    def draw_hline(x1, x2, y, color, thickness=3):
        for t in range(-thickness//2, thickness//2 + 1):
            py = y + t
            if 0 <= py < height:
                for x in range(x1, x2):
                    canvas[py][x] = color

    draw_hline(280, 380, 350, (148, 163, 184, 255), 4) # User -> CloudFront
    draw_hline(660, 780, 150, (34, 197, 94, 255), 4)  # CF -> S3 Assets
    draw_hline(660, 780, 350, (239, 68, 68, 255), 4)  # CF -> ALB
    draw_hline(660, 780, 550, (59, 130, 246, 255), 4) # CF -> S3 SPA

    def get_pixel(x, y, w, h):
        return canvas[y][x]

    png_bytes = create_png_rgba(width, height, get_pixel)
    with open(output_path, "wb") as f:
        f.write(png_bytes)
    print(f"✅ Arquivo PNG de arquitetura gerado: {output_path}")

if __name__ == "__main__":
    generate_architecture_png("architecture.png")
