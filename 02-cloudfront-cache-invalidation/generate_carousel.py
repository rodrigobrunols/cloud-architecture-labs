import os

class LightPDFBuilder:
    def __init__(self, width=1080, height=1080):
        self.width = width
        self.height = height
        self.pages = []

    def add_page(self, stream_cmds):
        stream_bytes = "\n".join(stream_cmds).encode("cp1252", "replace")
        stream_obj = f"<< /Length {len(stream_bytes)} >>\nstream\n{stream_bytes.decode('cp1252')}\nendstream"
        self.pages.append(stream_obj)

    def build(self, output_path):
        catalog_id = 1
        pages_id = 2
        font_helvetica_id = 3
        font_bold_id = 4
        font_mono_id = 5
        font_mono_bold_id = 6
        
        num_pages = len(self.pages)
        page_obj_ids = []
        content_obj_ids = []
        
        current_id = 7
        for i in range(num_pages):
            page_obj_ids.append(current_id)
            content_obj_ids.append(current_id + 1)
            current_id += 2
            
        obj1 = f"<< /Type /Catalog /Pages {pages_id} 0 R >>"
        kids_str = " ".join([f"{pid} 0 R" for pid in page_obj_ids])
        obj2 = f"<< /Type /Pages /Kids [ {kids_str} ] /Count {num_pages} >>"
        
        # Standard Adobe Fonts with WinAnsiEncoding (Full Portuguese Accent Support)
        obj3 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        obj4 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        obj5 = "<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
        obj6 = "<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>"
        
        all_objs = [obj1, obj2, obj3, obj4, obj5, obj6]
        
        for i in range(num_pages):
            p_id = page_obj_ids[i]
            c_id = content_obj_ids[i]
            
            p_obj = (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [ 0 0 {self.width} {self.height} ] "
                f"/Contents {c_id} 0 R "
                f"/Resources << /Font << "
                f"/F1 {font_helvetica_id} 0 R "
                f"/F2 {font_bold_id} 0 R "
                f"/F3 {font_mono_id} 0 R "
                f"/F4 {font_mono_bold_id} 0 R "
                f">> >> >>"
            )
            c_obj = self.pages[i]
            all_objs.extend([p_obj, c_obj])
            
        with open(output_path, "wb") as f:
            f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
            offsets = []
            
            for idx, obj in enumerate(all_objs, start=1):
                offsets.append(f.tell())
                f.write(f"{idx} 0 obj\n".encode("latin-1"))
                if isinstance(obj, str):
                    f.write(obj.encode("cp1252", "replace"))
                else:
                    f.write(obj)
                f.write(b"\nendobj\n")
                
            xref_offset = f.tell()
            f.write(f"xref\n0 {len(all_objs) + 1}\n".encode("latin-1"))
            f.write(b"0000000000 65535 f \n")
            for off in offsets:
                f.write(f"{off:010d} 00000 n \n".encode("latin-1"))
                
            f.write(
                f"trailer\n<< /Size {len(all_objs) + 1} /Root {catalog_id} 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
            )

# Drawing Primitives
def draw_rect(cmds, x, y, w, h, r_fill=None, g_fill=None, b_fill=None, r_stroke=None, g_stroke=None, b_stroke=None, line_width=1):
    cmds.append("q")
    if r_fill is not None:
        cmds.append(f"{r_fill:.3f} {g_fill:.3f} {b_fill:.3f} rg")
    if r_stroke is not None:
        cmds.append(f"{r_stroke:.3f} {g_stroke:.3f} {b_stroke:.3f} RG")
        cmds.append(f"{line_width} w")
    
    cmds.append(f"{x} {y} {w} {h} re")
    
    if r_fill is not None and r_stroke is not None:
        cmds.append("B")
    elif r_fill is not None:
        cmds.append("f")
    elif r_stroke is not None:
        cmds.append("S")
    cmds.append("Q")

def draw_circle(cmds, cx, cy, r, r_fill, g_fill, b_fill):
    k = 0.5522847498 * r
    cmds.append("q")
    cmds.append(f"{r_fill:.3f} {g_fill:.3f} {b_fill:.3f} rg")
    cmds.append(f"{cx + r} {cy} m")
    cmds.append(f"{cx + r} {cy + k} {cx + k} {cy + r} {cx} {cy + r} c")
    cmds.append(f"{cx - k} {cy + r} {cx - r} {cy + k} {cx - r} {cy} c")
    cmds.append(f"{cx - r} {cy - k} {cx - k} {cy - r} {cx} {cy - r} c")
    cmds.append(f"{cx + k} {cy - r} {cx + r} {cy - k} {cx + r} {cy} c")
    cmds.append("f")
    cmds.append("Q")

def draw_line(cmds, x1, y1, x2, y2, r_stroke=0.8, g_stroke=0.8, b_stroke=0.8, line_width=2):
    cmds.append("q")
    cmds.append(f"{r_stroke:.3f} {g_stroke:.3f} {b_stroke:.3f} RG")
    cmds.append(f"{line_width} w")
    cmds.append(f"{x1} {y1} m")
    cmds.append(f"{x2} {y2} l")
    cmds.append("S")
    cmds.append("Q")

def draw_text(cmds, text, x, y, font="F1", size=20, r=0.1, g=0.1, b=0.1):
    safe_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    cmds.append("BT")
    cmds.append(f"/{font} {size} Tf")
    cmds.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
    cmds.append(f"1 0 0 1 {x} {y} Tm")
    cmds.append(f"({safe_text}) Tj")
    cmds.append("ET")

def draw_slide_base_light(cmds, page_idx, total_pages=5, swipe_text="Arraste para o lado  ->"):
    # Pure White Background (#FFFFFF)
    draw_rect(cmds, 0, 0, 1080, 1080, 1.0, 1.0, 1.0)
    
    # Subtle Clean Grid Lines (#F1F5F9)
    for gy in range(120, 1000, 120):
        draw_rect(cmds, 80, gy, 920, 1, 0.94, 0.96, 0.98)
    for gx in range(160, 1000, 160):
        draw_rect(cmds, gx, 100, 1, 880, 0.94, 0.96, 0.98)
        
    # Top Accent Line (AWS Orange: #EA580C)
    draw_rect(cmds, 80, 995, 920, 4, 0.92, 0.35, 0.05)
    
    # Footer Divider (#E2E8F0)
    draw_rect(cmds, 80, 90, 920, 1, 0.88, 0.91, 0.94)
    
    # Footer Brand / Handle
    draw_circle(cmds, 98, 54, 14, 0.92, 0.35, 0.05)
    draw_text(cmds, "AWS", 86, 49, font="F2", size=10, r=1.0, g=1.0, b=1.0)
    draw_text(cmds, "AWS Architecture Series", 125, 48, font="F2", size=17, r=0.28, g=0.34, b=0.42)
    
    # Progress Dots
    dot_start_x = 500
    for p in range(1, total_pages + 1):
        if p == page_idx:
            draw_circle(cmds, dot_start_x + (p * 18), 54, 5, 0.92, 0.35, 0.05)
        else:
            draw_circle(cmds, dot_start_x + (p * 18), 54, 4, 0.80, 0.84, 0.88)
            
    # Page indicator & CTA
    if swipe_text:
        draw_text(cmds, swipe_text, 720, 48, font="F2", size=16, r=0.92, g=0.35, b=0.05)
    draw_text(cmds, f"{page_idx}/{total_pages}", 950, 48, font="F4", size=16, r=0.45, g=0.55, b=0.65)

def draw_pill_badge_light(cmds, text, x, y, badge_type="orange"):
    w = max(180, len(text) * 11 + 32)
    if badge_type == "orange":
        draw_rect(cmds, x, y, w, 36, 1.0, 0.96, 0.90, 0.92, 0.35, 0.05, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.80, g=0.28, b=0.02)
    elif badge_type == "red":
        draw_rect(cmds, x, y, w, 36, 1.0, 0.94, 0.94, 0.88, 0.20, 0.20, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.80, g=0.15, b=0.15)
    elif badge_type == "blue":
        draw_rect(cmds, x, y, w, 36, 0.93, 0.97, 1.0, 0.15, 0.45, 0.85, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.10, g=0.35, b=0.75)
    elif badge_type == "green":
        draw_rect(cmds, x, y, w, 36, 0.92, 0.98, 0.94, 0.10, 0.65, 0.40, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.08, g=0.50, b=0.30)

def draw_terminal_header_light(cmds, x, y, w, h=36, title="terminal - ci-cd-pipeline"):
    draw_rect(cmds, x, y, w, h, 0.94, 0.96, 0.98, 0.85, 0.88, 0.92, line_width=1)
    draw_circle(cmds, x + 20, y + 18, 6, 0.95, 0.35, 0.35)
    draw_circle(cmds, x + 40, y + 18, 6, 0.95, 0.75, 0.25)
    draw_circle(cmds, x + 60, y + 18, 6, 0.35, 0.85, 0.45)
    if title:
        draw_text(cmds, title, x + 85, y + 12, font="F3", size=13, r=0.40, g=0.48, b=0.58)

def build_light_carousel():
    pdf = LightPDFBuilder(1080, 1080)
    
    # =========================================================================
    # SLIDE 1: CAPA (Fundo Branco & Tipografia Editorial)
    # =========================================================================
    s1 = []
    draw_slide_base_light(s1, 1, 5, swipe_text="Arraste para o lado  ->")
    draw_pill_badge_light(s1, "AWS ARCHITECTURE & CI/CD", 80, 920, "orange")
    
    draw_text(s1, "Você ainda roda", 80, 810, font="F2", size=50, r=0.06, g=0.09, b=0.16)
    draw_text(s1, "INVALIDAÇÃO /* NO CLOUDFRONT?", 80, 740, font="F2", size=44, r=0.92, g=0.35, b=0.05)
    
    # Terminal Box Light
    t_y = 350
    draw_terminal_header_light(s1, 80, t_y + 240, 920, 38, title="terminal - cloudfront-invalidation")
    draw_rect(s1, 80, t_y, 920, 240, 0.98, 0.99, 1.0, 0.85, 0.88, 0.92, line_width=1)
    
    draw_text(s1, "# 'Cache invalidation is one of the 2 hard things' - Phil Karlton", 115, t_y + 195, font="F3", size=18, r=0.45, g=0.52, b=0.60)
    draw_text(s1, "$ aws cloudfront create-invalidation \\", 115, t_y + 155, font="F4", size=20, r=0.10, g=0.40, b=0.80)
    draw_text(s1, "    --distribution-id $CF_ID \\", 115, t_y + 120, font="F3", size=19, r=0.15, g=0.20, b=0.28)
    draw_text(s1, "    --paths '/index.html' '/'", 115, t_y + 85, font="F4", size=20, r=0.08, g=0.55, b=0.32)
    draw_text(s1, "-> Invalidação cirúrgica: 0 downtime, 100% de cache hit nos chunks!", 115, t_y + 40, font="F2", size=18, r=0.08, g=0.55, b=0.32)
    
    # Subtitle Box
    draw_rect(s1, 80, 180, 920, 130, 0.96, 0.98, 1.0, 0.15, 0.45, 0.85, line_width=1.5)
    draw_text(s1, "Aprenda a sincronizar React + APIs dinâmicas no CI/CD", 115, 255, font="F2", size=24, r=0.06, g=0.09, b=0.16)
    draw_text(s1, "evitando telas brancas (404), sobrecarga de backend e custos extras.", 115, 215, font="F1", size=21, r=0.28, g=0.34, b=0.42)
    
    pdf.add_page(s1)
    
    # =========================================================================
    # SLIDE 2: O ERRO CLÁSSICO (Light Mode)
    # =========================================================================
    s2 = []
    draw_slide_base_light(s2, 2, 5, swipe_text="Arraste  ->")
    draw_pill_badge_light(s2, "O ERRO DE ARQUITETURA", 80, 920, "red")
    
    draw_text(s2, "Por que invalidar /* a cada", 80, 835, font="F2", size=42, r=0.06, g=0.09, b=0.16)
    draw_text(s2, "deploy é um ANTI-PATTERN?", 80, 780, font="F2", size=46, r=0.92, g=0.35, b=0.05)
    
    # Split Cards
    # Left Card: Invalidar /*
    draw_rect(s2, 80, 430, 440, 310, 1.0, 1.0, 1.0, 0.88, 0.20, 0.20, line_width=2)
    draw_rect(s2, 80, 690, 440, 50, 1.0, 0.94, 0.94)
    draw_text(s2, "❌ Purgar Tudo (/*)", 105, 708, font="F2", size=22, r=0.80, g=0.15, b=0.15)
    
    draw_text(s2, "• Cache Hit Ratio despenca para ZERO.", 105, 645, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "• Efeito Manada: Milhares de clientes", 105, 605, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "  buscam tudo no S3/Origem de vez.", 105, 580, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "• Risco de Tela Branca (404) para quem", 105, 535, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "  estava navegando durante o build.", 105, 510, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "• Ultrapassa os 1.000 caminhos grátis/mês.", 105, 460, font="F2", size=17, r=0.80, g=0.15, b=0.15)
    
    # Right Card: Cache-Busting + Invalidação Cirúrgica
    draw_rect(s2, 560, 430, 440, 310, 1.0, 1.0, 1.0, 0.10, 0.65, 0.40, line_width=2)
    draw_rect(s2, 560, 690, 440, 50, 0.92, 0.98, 0.94)
    draw_text(s2, "✅ Invalidação Cirúrgica", 585, 708, font="F2", size=22, r=0.08, g=0.50, b=0.30)
    
    draw_text(s2, "• Chunks JS/CSS usam HASH no nome.", 585, 645, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "• Cache de 1 ano (immutable) na Edge.", 585, 605, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "• Usuários antigos terminam a sessão", 585, 565, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "  nos chunks antigos sem nenhum erro.", 585, 540, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    draw_text(s2, "• Invalida SOMENTE o /index.html.", 585, 495, font="F2", size=18, r=0.08, g=0.50, b=0.30)
    draw_text(s2, "• Custo zero e velocidade máxima!", 585, 460, font="F2", size=17, r=0.08, g=0.50, b=0.30)
    
    # Golden Rule Box
    draw_rect(s2, 80, 180, 920, 210, 0.96, 0.98, 1.0, 0.15, 0.45, 0.85, line_width=2)
    draw_text(s2, "💡 REGRA DE OURO: CACHE BUSTING > INVALIDATION", 115, 340, font="F2", size=22, r=0.92, g=0.35, b=0.05)
    draw_text(s2, "Se o nome do arquivo muda a cada alteração (ex: main.a8f9.js),", 115, 285, font="F2", size=23, r=0.06, g=0.09, b=0.16)
    draw_text(s2, "ele NUNCA precisa ser invalidado no CloudFront.", 115, 235, font="F2", size=23, r=0.10, g=0.40, b=0.80)
    
    pdf.add_page(s2)
    
    # =========================================================================
    # SLIDE 3: O CONCEITO (Os 3 Pilares de Caching)
    # =========================================================================
    s3 = []
    draw_slide_base_light(s3, 3, 5, swipe_text="Arraste  ->")
    draw_pill_badge_light(s3, "ESTRATÉGIA DE CABEÇALHOS", 80, 920, "blue")
    
    draw_text(s3, "A Estratégia dos", 80, 835, font="F2", size=42, r=0.06, g=0.09, b=0.16)
    draw_text(s3, "3 PILARES DE CACHE", 80, 780, font="F2", size=48, r=0.10, g=0.40, b=0.80)
    draw_text(s3, "Como configurar o Cache-Control correto para cada tipo de arquivo no S3/API:", 80, 720, font="F1", size=20, r=0.28, g=0.34, b=0.42)
    
    # Card 1: Hashed Assets
    draw_rect(s3, 80, 520, 920, 160, 1.0, 1.0, 1.0, 0.10, 0.65, 0.40, line_width=2)
    draw_rect(s3, 80, 640, 920, 40, 0.92, 0.98, 0.94)
    draw_text(s3, "1. Bundles Hashed (/assets/*.js, *.css)", 115, 652, font="F2", size=20, r=0.08, g=0.50, b=0.30)
    draw_text(s3, "Cache-Control: public, max-age=31536000, immutable", 115, 595, font="F4", size=18, r=0.10, g=0.40, b=0.80)
    draw_text(s3, "• Fica em cache na Edge por 1 ano. Nunca invalide.", 115, 550, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    
    # Card 2: Entrypoint HTML
    draw_rect(s3, 80, 340, 920, 160, 1.0, 1.0, 1.0, 0.92, 0.35, 0.05, line_width=2)
    draw_rect(s3, 80, 460, 920, 40, 1.0, 0.96, 0.90)
    draw_text(s3, "2. Entrypoint SPA (index.html)", 115, 472, font="F2", size=20, r=0.80, g=0.28, b=0.02)
    draw_text(s3, "Cache-Control: public, max-age=0, must-revalidate", 115, 415, font="F4", size=18, r=0.92, g=0.35, b=0.05)
    draw_text(s3, "• O navegador sempre checa se há nova versão. Invalidação cirúrgica!", 115, 370, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    
    # Card 3: Backend APIs
    draw_rect(s3, 80, 160, 920, 160, 1.0, 1.0, 1.0, 0.15, 0.45, 0.85, line_width=2)
    draw_rect(s3, 80, 280, 920, 40, 0.93, 0.97, 1.0)
    draw_text(s3, "3. Backend APIs (/api/cart, /api/catalog)", 115, 292, font="F2", size=20, r=0.10, g=0.35, b=0.75)
    draw_text(s3, "Cart/Auth: no-store | Catálogo: s-maxage=60, stale-while-revalidate=300", 115, 235, font="F4", size=17, r=0.80, g=0.15, b=0.15)
    draw_text(s3, "• Garante dados frescos em transações e alta escala no catálogo.", 115, 190, font="F1", size=18, r=0.20, g=0.25, b=0.32)
    
    pdf.add_page(s3)
    
    # =========================================================================
    # SLIDE 4: DIAGRAMA VISUAL DO PIPELINE CI/CD
    # =========================================================================
    s4 = []
    draw_slide_base_light(s4, 4, 5, swipe_text="Arraste  ->")
    draw_pill_badge_light(s4, "FLUXO NO PIPELINE CI/CD", 80, 920, "green")
    
    draw_text(s4, "O Pipeline de Deploy Perfeito", 80, 835, font="F2", size=38, r=0.06, g=0.09, b=0.16)
    draw_text(s4, "GitHub Actions / GitLab CI -> AWS S3 & CloudFront", 80, 785, font="F2", size=26, r=0.08, g=0.50, b=0.30)
    
    # Diagram Canvas Box
    draw_rect(s4, 80, 140, 920, 610, 0.98, 0.99, 1.0, 0.85, 0.88, 0.92, line_width=1.5)
    
    # Step 1: Build
    draw_rect(s4, 110, 560, 860, 140, 1.0, 1.0, 1.0, 0.15, 0.45, 0.85, line_width=2)
    draw_rect(s4, 110, 660, 860, 40, 0.93, 0.97, 1.0)
    draw_text(s4, "PASSO 1: Build da Aplicação React / Vite", 130, 672, font="F2", size=18, r=0.10, g=0.35, b=0.75)
    draw_text(s4, "$ npm run build   # Gera index.html e /assets/app.[hash].js", 130, 615, font="F4", size=17, r=0.15, g=0.20, b=0.28)
    draw_text(s4, "-> Cria artefatos com hashes exclusivos no diretório dist/", 130, 578, font="F1", size=15, r=0.40, g=0.48, b=0.58)
    
    # Step 2: Sync Hashed Assets (Exclude index.html)
    draw_rect(s4, 110, 390, 860, 150, 1.0, 1.0, 1.0, 0.10, 0.65, 0.40, line_width=2)
    draw_rect(s4, 110, 500, 860, 40, 0.92, 0.98, 0.94)
    draw_text(s4, "PASSO 2: Sincronizar Chunks PRIMEIRO (Sem index.html)", 130, 512, font="F2", size=18, r=0.08, g=0.50, b=0.30)
    draw_text(s4, "$ aws s3 sync dist/ s3://$BUCKET/ --exclude 'index.html' \\", 130, 462, font="F4", size=16, r=0.15, g=0.20, b=0.28)
    draw_text(s4, "    --cache-control 'public, max-age=31536000, immutable'", 130, 432, font="F4", size=16, r=0.08, g=0.50, b=0.30)
    draw_text(s4, "-> Garante que todos os novos arquivos JS/CSS já estão disponíveis no S3.", 130, 402, font="F1", size=14, r=0.40, g=0.48, b=0.58)
    
    # Step 3 & 4: Upload index.html + Invalidate
    draw_rect(s4, 110, 160, 860, 210, 1.0, 1.0, 1.0, 0.92, 0.35, 0.05, line_width=2)
    draw_rect(s4, 110, 330, 860, 40, 1.0, 0.96, 0.90)
    draw_text(s4, "PASSO 3 & 4: Subir index.html + Invalidação Cirúrgica", 130, 342, font="F2", size=18, r=0.80, g=0.28, b=0.02)
    draw_text(s4, "$ aws s3 cp dist/index.html s3://$BUCKET/index.html \\", 130, 290, font="F4", size=16, r=0.15, g=0.20, b=0.28)
    draw_text(s4, "    --cache-control 'public, max-age=0, must-revalidate'", 130, 262, font="F4", size=16, r=0.92, g=0.35, b=0.05)
    draw_text(s4, "$ aws cloudfront create-invalidation --dist-id $CF_ID --paths '/index.html'", 130, 222, font="F4", size=16, r=0.10, g=0.40, b=0.80)
    draw_text(s4, "-> 0 telas brancas, propagação imediata e menor privilégio no IAM!", 130, 182, font="F2", size=16, r=0.08, g=0.50, b=0.30)
    
    pdf.add_page(s4)
    
    # =========================================================================
    # SLIDE 5: A PEGADINHA & SALVAMENTO
    # =========================================================================
    s5 = []
    draw_slide_base_light(s5, 5, 5, swipe_text="")
    draw_pill_badge_light(s5, "ATENÇÃO EM PRODUÇÃO", 80, 920, "orange")
    
    draw_text(s5, "A Pegadinha da", 80, 835, font="F2", size=42, r=0.06, g=0.09, b=0.16)
    draw_text(s5, "ORDEM DE DEPLOY!", 80, 780, font="F2", size=50, r=0.92, g=0.35, b=0.05)
    
    # Priority Visual Box
    draw_rect(s5, 80, 420, 920, 310, 1.0, 1.0, 1.0, 0.92, 0.35, 0.05, line_width=2)
    draw_rect(s5, 80, 680, 920, 50, 1.0, 0.96, 0.90)
    draw_text(s5, "POR QUE A ORDEM IMPORTA NO PIPELINE? ⏱️", 115, 698, font="F2", size=22, r=0.80, g=0.28, b=0.02)
    
    draw_text(s5, "Se você subir o index.html ANTES dos novos arquivos JS:", 115, 635, font="F2", size=22, r=0.80, g=0.15, b=0.15)
    draw_text(s5, "1. O usuário baixa o novo index.html imediatamente.", 115, 580, font="F1", size=19, r=0.20, g=0.25, b=0.32)
    draw_text(s5, "2. O HTML pede o chunk 'app.new-hash.js' que ainda está subindo.", 115, 540, font="F1", size=19, r=0.20, g=0.25, b=0.32)
    draw_text(s5, "3. O S3 retorna 404 e o CloudFront pode cachear o erro!", 115, 500, font="F4", size=19, r=0.80, g=0.15, b=0.15)
    draw_text(s5, "4. Resultado: O cliente vê uma tela branca quebrada.", 115, 455, font="F2", size=20, r=0.80, g=0.15, b=0.15)
    
    # Bookmark Box
    draw_rect(s5, 80, 160, 920, 210, 0.94, 0.98, 0.95, 0.10, 0.65, 0.40, line_width=2)
    draw_text(s5, "📌 SALVE ESTE POST!", 115, 315, font="F2", size=26, r=0.08, g=0.50, b=0.30)
    draw_text(s5, "Guarde para configurar seus pipelines de CI/CD (GitHub Actions / GitLab)", 115, 260, font="F1", size=21, r=0.06, g=0.09, b=0.16)
    draw_text(s5, "com a melhor performance e zero downtime na AWS.", 115, 215, font="F1", size=21, r=0.28, g=0.34, b=0.42)
    
    pdf.add_page(s5)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "carrossel_cloudfront_cache_invalidation.pdf")
    pdf.build(output_file)
    print(f"✅ Sucesso! PDF do carrossel gerado em: {output_file} ({os.path.getsize(output_file)} bytes)")

if __name__ == "__main__":
    build_light_carousel()
