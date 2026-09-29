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

def generate_invalidation_png(output_path):
    width, height = 1200, 700
    
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

    # Box 1: CI/CD Pipeline (Left)
    fill_rect(60, 200, 260, 300, (239, 246, 255, 255), (59, 130, 246, 255), 2)
    # Box 2: AWS S3 Frontend Bucket (Middle Top)
    fill_rect(420, 100, 340, 200, (240, 253, 244, 255), (34, 197, 94, 255), 2)
    # Box 3: CloudFront Distribution (Right)
    fill_rect(860, 180, 280, 340, (255, 251, 235, 255), (255, 153, 0, 255), 3)
    # Box 4: Backend API (Middle Bottom)
    fill_rect(420, 390, 340, 200, (254, 242, 242, 255), (239, 68, 68, 255), 2)

    # Connecting lines / Arrows (horizontal bands)
    def draw_hline(x1, x2, y, color, thickness=3):
        for t in range(-thickness//2, thickness//2 + 1):
            py = y + t
            if 0 <= py < height:
                for x in range(x1, x2):
                    canvas[py][x] = color

    draw_hline(320, 420, 200, (34, 197, 94, 255), 4)  # CI/CD -> S3 (Sync)
    draw_hline(760, 860, 200, (34, 197, 94, 255), 4)  # S3 -> CloudFront
    draw_hline(320, 860, 490, (255, 153, 0, 255), 4)  # CI/CD -> CloudFront (Invalidate /index.html)
    draw_hline(760, 860, 490, (239, 68, 68, 255), 4)  # ALB -> CloudFront

    def get_pixel(x, y, w, h):
        return canvas[y][x]

    png_bytes = create_png_rgba(width, height, get_pixel)
    with open(output_path, "wb") as f:
        f.write(png_bytes)
    print(f"✅ Arquivo PNG de invalidação gerado: {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generate_invalidation_png(os.path.join(script_dir, "invalidation.png"))
    generate_invalidation_png(os.path.join(script_dir, "architecture.png"))
