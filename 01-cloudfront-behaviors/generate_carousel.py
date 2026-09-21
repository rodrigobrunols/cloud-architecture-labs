import os

class CleanPDFBuilder:
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
        
        # Adobe Core 14 Fonts with WinAnsiEncoding (Full Portuguese Accent Support)
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

def draw_text(cmds, text, x, y, font="F1", size=20, r=1.0, g=1.0, b=1.0):
    safe_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    cmds.append("BT")
    cmds.append(f"/{font} {size} Tf")
    cmds.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
    cmds.append(f"1 0 0 1 {x} {y} Tm")
    cmds.append(f"({safe_text}) Tj")
    cmds.append("ET")

def draw_terminal_header(cmds, x, y, w, h=36, title="bash - aws-cli"):
    draw_rect(cmds, x, y, w, h, 0.08, 0.10, 0.15, 0.18, 0.22, 0.30, line_width=1)
    draw_circle(cmds, x + 20, y + 18, 6, 0.95, 0.35, 0.35)
    draw_circle(cmds, x + 40, y + 18, 6, 0.95, 0.75, 0.25)
    draw_circle(cmds, x + 60, y + 18, 6, 0.35, 0.85, 0.45)
    if title:
        draw_text(cmds, title, x + 85, y + 12, font="F3", size=13, r=0.55, g=0.62, b=0.72)

def draw_slide_base(cmds, page_idx, total_pages=5, swipe_text="Arraste para o lado  ->"):
    draw_rect(cmds, 0, 0, 1080, 1080, 0.043, 0.060, 0.098)
    
    for gy in range(120, 1000, 120):
        draw_rect(cmds, 80, gy, 920, 1, 0.07, 0.09, 0.14)
    for gx in range(160, 1000, 160):
        draw_rect(cmds, gx, 100, 1, 880, 0.07, 0.09, 0.14)
        
    draw_rect(cmds, 80, 995, 920, 3, 1.0, 0.60, 0.0)
    draw_rect(cmds, 80, 90, 920, 1, 0.18, 0.22, 0.30)
    
    draw_circle(cmds, 98, 54, 14, 1.0, 0.60, 0.0)
    draw_text(cmds, "AWS", 86, 49, font="F2", size=10, r=0.04, g=0.06, b=0.1)
    draw_text(cmds, "AWS Architecture Series", 125, 48, font="F2", size=17, r=0.65, g=0.72, b=0.82)
    
    dot_start_x = 500
    for p in range(1, total_pages + 1):
        if p == page_idx:
            draw_circle(cmds, dot_start_x + (p * 18), 54, 5, 1.0, 0.60, 0.0)
        else:
            draw_circle(cmds, dot_start_x + (p * 18), 54, 4, 0.25, 0.30, 0.40)
            
    if swipe_text:
        draw_text(cmds, swipe_text, 720, 48, font="F2", size=16, r=1.0, g=0.60, b=0.0)
    draw_text(cmds, f"{page_idx}/{total_pages}", 950, 48, font="F4", size=16, r=0.65, g=0.72, b=0.82)

def draw_pill_badge(cmds, text, x, y, bg_color="orange"):
    w = max(180, len(text) * 11 + 32)
    if bg_color == "orange":
        draw_rect(cmds, x, y, w, 36, 0.16, 0.10, 0.04, 1.0, 0.60, 0.0, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=1.0, g=0.60, b=0.0)
    elif bg_color == "red":
        draw_rect(cmds, x, y, w, 36, 0.18, 0.06, 0.06, 0.95, 0.40, 0.40, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.95, g=0.40, b=0.40)
    elif bg_color == "blue":
        draw_rect(cmds, x, y, w, 36, 0.06, 0.14, 0.22, 0.22, 0.74, 0.97, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.22, g=0.74, b=0.97)
    elif bg_color == "green":
        draw_rect(cmds, x, y, w, 36, 0.06, 0.16, 0.10, 0.20, 0.83, 0.60, line_width=1.5)
        draw_text(cmds, text, x + 16, y + 11, font="F4", size=14, r=0.20, g=0.83, b=0.60)

def build_carousel_pdf():
    pdf = CleanPDFBuilder(1080, 1080)
    
    # -------------------------------------------------------------
    # SLIDE 1: CAPA
    # -------------------------------------------------------------
    s1 = []
    draw_slide_base(s1, 1, 5, swipe_text="Arraste para o lado  ->")
    draw_pill_badge(s1, "AWS ARCHITECTURE ESSENTIALS", 80, 920, "orange")
    
    draw_text(s1, "Você sabe o que é", 80, 810, font="F2", size=52, r=1.0, g=1.0, b=1.0)
    draw_text(s1, "BEHAVIOR na AWS?", 80, 735, font="F2", size=60, r=1.0, g=0.60, b=0.0)
    
    t_y = 350
    draw_terminal_header(s1, 80, t_y + 240, 920, 38, title="terminal - cloudfront-architecture")
    draw_rect(s1, 80, t_y, 920, 240, 0.06, 0.08, 0.12, 0.18, 0.22, 0.30, line_width=1)
    
    draw_text(s1, "# Como desacoplar containers Docker e economizar CPU:", 115, t_y + 195, font="F3", size=19, r=0.45, g=0.55, b=0.68)
    draw_text(s1, "$ aws cloudfront create-distribution \\", 115, t_y + 155, font="F4", size=20, r=0.22, g=0.74, b=0.97)
    draw_text(s1, "    --origins Id=S3-Assets,Id=ALB-Backend \\", 115, t_y + 120, font="F3", size=19, r=0.85, g=0.90, b=0.95)
    draw_text(s1, "    --default-cache-behavior TargetOriginId=S3-Assets", 115, t_y + 85, font="F3", size=19, r=0.85, g=0.90, b=0.95)
    draw_text(s1, "-> Roteamento na Edge com múltiplas origens e zero desperdício.", 115, t_y + 40, font="F2", size=19, r=0.20, g=0.83, b=0.60)
    
    draw_rect(s1, 80, 180, 920, 130, 0.08, 0.11, 0.17, 0.22, 0.74, 0.97, line_width=1.5)
    draw_text(s1, "Aprenda como dividir tráfego de imagens e APIs dinâmicas", 115, 255, font="F2", size=24, r=1.0, g=1.0, b=1.0)
    draw_text(s1, "usando um único domínio, acelerando o carregamento da sua aplicação.", 115, 215, font="F1", size=21, r=0.80, g=0.85, b=0.92)
    
    pdf.add_page(s1)
    
    # -------------------------------------------------------------
    # SLIDE 2: O ERRO CLÁSSICO
    # -------------------------------------------------------------
    s2 = []
    draw_slide_base(s2, 2, 5, swipe_text="Arraste  ->")
    draw_pill_badge(s2, "O ERRO DE ARQUITETURA", 80, 920, "red")
    
    draw_text(s2, "Não queime CPU cara com", 80, 835, font="F2", size=42, r=1.0, g=1.0, b=1.0)
    draw_text(s2, "arquivos estáticos!", 80, 780, font="F2", size=46, r=1.0, g=0.60, b=0.0)
    
    draw_rect(s2, 80, 440, 440, 290, 0.07, 0.09, 0.13, 0.95, 0.40, 0.40, line_width=2)
    draw_rect(s2, 80, 680, 440, 50, 0.14, 0.06, 0.06)
    draw_text(s2, "❌ No Container Docker", 105, 698, font="F2", size=22, r=0.95, g=0.40, b=0.40)
    
    draw_text(s2, "• Imagem incha de 80MB para 1.5GB+", 105, 635, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• Servidor gasta CPU/RAM caras", 105, 595, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "  apenas lendo arquivos do disco.", 105, 570, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• Auto Scaling lento na Black Friday.", 105, 525, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• Uploads de usuários somem se reiniciar.", 105, 475, font="F2", size=17, r=0.95, g=0.40, b=0.40)
    
    draw_rect(s2, 560, 440, 440, 290, 0.07, 0.09, 0.13, 0.20, 0.83, 0.60, line_width=2)
    draw_rect(s2, 560, 680, 440, 50, 0.06, 0.14, 0.10)
    draw_text(s2, "✅ No S3 + CloudFront", 585, 698, font="F2", size=22, r=0.20, g=0.83, b=0.60)
    
    draw_text(s2, "• Imagem Docker limpa e rápida (<100MB).", 585, 635, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• Entrega na Edge em milissegundos.", 585, 595, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• 99.999999999% de durabilidade.", 585, 555, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• Custo de centavos por GB armazenado.", 585, 515, font="F1", size=18, r=0.85, g=0.90, b=0.95)
    draw_text(s2, "• Container 100% focado na API.", 585, 475, font="F2", size=17, r=0.20, g=0.83, b=0.60)
    
    draw_rect(s2, 80, 180, 920, 210, 0.05, 0.12, 0.18, 0.22, 0.74, 0.97, line_width=2)
    draw_text(s2, "💡 REGRA DE OURO DA ARQUITETURA MODERNA", 115, 340, font="F2", size=22, r=1.0, g=0.60, b=0.0)
    draw_text(s2, "Container processa regra de negócio (CPU & Memória).", 115, 285, font="F2", size=24, r=1.0, g=1.0, b=1.0)
    draw_text(s2, "Amazon S3 + CloudFront entregam e armazenam arquivos estáticos.", 115, 235, font="F2", size=23, r=0.22, g=0.74, b=0.97)
    
    pdf.add_page(s2)
    
    # -------------------------------------------------------------
    # SLIDE 3: O CONCEITO
    # -------------------------------------------------------------
    s3 = []
    draw_slide_base(s3, 3, 5, swipe_text="Arraste  ->")
    draw_pill_badge(s3, "CONCEITO CHAVE", 80, 920, "blue")
    
    draw_text(s3, "O que é o CloudFront", 80, 835, font="F2", size=42, r=1.0, g=1.0, b=1.0)
    draw_text(s3, "BEHAVIOR?", 80, 780, font="F2", size=48, r=0.22, g=0.74, b=0.97)
    draw_text(s3, "É a regra de trânsito na Edge que inspeciona a URL de cada requisição.", 80, 720, font="F1", size=22, r=0.80, g=0.85, b=0.92)
    
    draw_rect(s3, 80, 470, 920, 200, 0.07, 0.09, 0.13, 1.0, 0.60, 0.0, line_width=2)
    draw_rect(s3, 80, 620, 920, 50, 0.14, 0.09, 0.04)
    draw_text(s3, "1. Origem de Destino (Routing)", 115, 638, font="F2", size=24, r=1.0, g=0.60, b=0.0)
    draw_text(s3, "Define para qual backend a rota será enviada:", 115, 575, font="F1", size=21, r=0.85, g=0.90, b=0.95)
    draw_text(s3, "• Bucket Amazon S3 (para fotos, banners e front-end SPA)", 115, 535, font="F2", size=20, r=1.0, g=1.0, b=1.0)
    draw_text(s3, "• Application Load Balancer / API Gateway (para microsserviços)", 115, 495, font="F2", size=20, r=0.22, g=0.74, b=0.97)
    
    draw_rect(s3, 80, 200, 920, 220, 0.07, 0.09, 0.13, 0.22, 0.74, 0.97, line_width=2)
    draw_rect(s3, 80, 370, 920, 50, 0.05, 0.12, 0.18)
    draw_text(s3, "2. Política de Cache e Headers (Cache Policy)", 115, 388, font="F2", size=24, r=0.22, g=0.74, b=0.97)
    draw_text(s3, "Define se a resposta fica em cache e por quanto tempo:", 115, 325, font="F1", size=21, r=0.85, g=0.90, b=0.95)
    draw_text(s3, "• Imagens & Assets: Cache agressivo (TTL de 1 ano, compressão Brotli).", 115, 285, font="F2", size=20, r=1.0, g=1.0, b=1.0)
    draw_text(s3, "• Checkout & APIs: Cache ZERO (TTL=0, repassa Cookies e Auth).", 115, 245, font="F2", size=20, r=0.95, g=0.40, b=0.40)
    
    pdf.add_page(s3)
    
    # -------------------------------------------------------------
    # SLIDE 4: CENÁRIO REAL
    # -------------------------------------------------------------
    s4 = []
    draw_slide_base(s4, 4, 5, swipe_text="Arraste  ->")
    draw_pill_badge(s4, "ARQUITETURA NA PRÁTICA", 80, 920, "green")
    
    draw_text(s4, "Roteamento Inteligente em", 80, 835, font="F2", size=42, r=1.0, g=1.0, b=1.0)
    draw_text(s4, "1 Único Domínio (mystore.com)", 80, 780, font="F2", size=46, r=0.20, g=0.83, b=0.60)
    
    draw_rect(s4, 80, 560, 920, 175, 0.07, 0.09, 0.13, 0.20, 0.83, 0.60, line_width=2)
    draw_text(s4, "PATH PATTERN", 115, 695, font="F4", size=14, r=0.55, g=0.65, b=0.75)
    draw_text(s4, "/images/*  &  /static/*", 115, 655, font="F4", size=25, r=0.22, g=0.74, b=0.97)
    draw_text(s4, "DESTINO: Bucket S3", 640, 655, font="F2", size=22, r=1.0, g=0.60, b=0.0)
    draw_text(s4, "Cache longo (1 ano) + Gzip/Brotli. Alívio total para o backend.", 115, 600, font="F1", size=20, r=0.85, g=0.90, b=0.95)
    
    draw_rect(s4, 80, 350, 920, 175, 0.07, 0.09, 0.13, 0.95, 0.40, 0.40, line_width=2)
    draw_text(s4, "PATH PATTERN", 115, 485, font="F4", size=14, r=0.55, g=0.65, b=0.75)
    draw_text(s4, "/api/checkout/*  &  /api/cart/*", 115, 445, font="F4", size=25, r=0.22, g=0.74, b=0.97)
    draw_text(s4, "DESTINO: Container (ALB)", 610, 445, font="F2", size=22, r=0.95, g=0.40, b=0.40)
    draw_text(s4, "Cache ZERO. Repassa Headers, Cookies e métodos POST/PUT/DELETE.", 115, 390, font="F1", size=20, r=0.85, g=0.90, b=0.95)
    
    draw_rect(s4, 80, 140, 920, 175, 0.07, 0.09, 0.13, 0.22, 0.74, 0.97, line_width=2)
    draw_text(s4, "PATH PATTERN", 115, 275, font="F4", size=14, r=0.55, g=0.65, b=0.75)
    draw_text(s4, "Default (*)", 115, 235, font="F4", size=25, r=0.22, g=0.74, b=0.97)
    draw_text(s4, "DESTINO: Bucket S3", 640, 235, font="F2", size=22, r=1.0, g=0.60, b=0.0)
    draw_text(s4, "Entrega o index.html da Single Page App (React, Vue, Angular).", 115, 180, font="F1", size=20, r=0.85, g=0.90, b=0.95)
    
    pdf.add_page(s4)
    
    # -------------------------------------------------------------
    # SLIDE 5: A PEGADINHA
    # -------------------------------------------------------------
    s5 = []
    draw_slide_base(s5, 5, 5, swipe_text="")
    draw_pill_badge(s5, "ATENÇÃO EM PRODUÇÃO", 80, 920, "orange")
    
    draw_text(s5, "Cuidado com a Ordem de", 80, 835, font="F2", size=42, r=1.0, g=1.0, b=1.0)
    draw_text(s5, "PRECEDÊNCIA!", 80, 780, font="F2", size=50, r=1.0, g=0.60, b=0.0)
    
    draw_rect(s5, 80, 420, 920, 310, 0.07, 0.09, 0.13, 1.0, 0.60, 0.0, line_width=2)
    draw_rect(s5, 80, 680, 920, 50, 0.14, 0.09, 0.04)
    draw_text(s5, "AVALIAÇÃO DE CIMA PARA BAIXO (Top to Bottom) ⬇️", 115, 698, font="F2", size=22, r=1.0, g=0.60, b=0.0)
    
    draw_text(s5, "O CloudFront para na PRIMEIRA regra correspondente.", 115, 635, font="F2", size=23, r=1.0, g=1.0, b=1.0)
    draw_text(s5, "• Precedência 0:  /images/*       -> Avaliado primeiro", 115, 580, font="F4", size=20, r=0.20, g=0.83, b=0.60)
    draw_text(s5, "• Precedência 1:  /api/*          -> Avaliado em seguida", 115, 540, font="F4", size=20, r=0.22, g=0.74, b=0.97)
    draw_text(s5, "• Precedência 2:  Default (*)     -> Fallback final", 115, 500, font="F4", size=20, r=0.95, g=0.40, b=0.40)
    draw_text(s5, "Se colocar o coringa (*) no topo, ele anula todas as outras regras!", 115, 455, font="F2", size=20, r=0.95, g=0.40, b=0.40)
    
    draw_rect(s5, 80, 160, 920, 210, 0.06, 0.14, 0.10, 0.20, 0.83, 0.60, line_width=2)
    draw_text(s5, "📌 SALVE ESTE POST!", 115, 315, font="F2", size=26, r=0.20, g=0.83, b=0.60)
    draw_text(s5, "Deixe guardado para consultar quando for desenhar ou revisar", 115, 260, font="F1", size=22, r=1.0, g=1.0, b=1.0)
    draw_text(s5, "sua próxima arquitetura de microsserviços na AWS.", 115, 215, font="F1", size=22, r=0.85, g=0.90, b=0.95)
    
    pdf.add_page(s5)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "carrossel_cloudfront_behaviors.pdf")
    pdf.build(output_file)
    print(f"Sucesso! PDF compilado em: {output_file} ({os.path.getsize(output_file)} bytes)")

if __name__ == "__main__":
    build_carousel_pdf()
