import subprocess
import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

  @page {
    size: 1080px 1080px;
    margin: 0;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Plus Jakarta Sans', 'Segoe UI', Roboto, sans-serif;
    background-color: #0B0F19;
    color: #F8FAFC;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .slide {
    width: 1080px;
    height: 1080px;
    page-break-after: always;
    position: relative;
    padding: 75px 85px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    background: radial-gradient(circle at 85% 15%, rgba(255, 153, 0, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 15% 85%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                #0B0F19;
  }

  /* Grid overlay effect */
  .slide::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
  }

  /* Header Badge */
  .tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 153, 0, 0.12);
    border: 1px solid rgba(255, 153, 0, 0.35);
    color: #FF9900;
    padding: 8px 18px;
    border-radius: 9999px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    width: fit-content;
  }

  .tag.blue {
    background: rgba(56, 189, 248, 0.12);
    border-color: rgba(56, 189, 248, 0.35);
    color: #38BDF8;
  }

  .tag.red {
    background: rgba(248, 113, 113, 0.12);
    border-color: rgba(248, 113, 113, 0.35);
    color: #F87171;
  }

  .tag.green {
    background: rgba(52, 211, 153, 0.12);
    border-color: rgba(52, 211, 153, 0.35);
    color: #34D399;
  }

  /* Typography */
  h1 {
    font-size: 58px;
    font-weight: 800;
    line-height: 1.15;
    color: #FFFFFF;
    letter-spacing: -1px;
  }

  .highlight-orange {
    color: #FF9900;
  }

  .highlight-blue {
    color: #38BDF8;
  }

  .subtitle {
    font-size: 26px;
    color: #94A3B8;
    line-height: 1.45;
    font-weight: 500;
  }

  /* Cards & Containers */
  .card {
    background: rgba(30, 41, 59, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 32px 36px;
    backdrop-filter: blur(10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }

  .card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  .card-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .card-desc {
    font-size: 20px;
    color: #CBD5E1;
    line-height: 1.45;
  }

  /* Route Box for Slide 4 */
  .route-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 18px;
  }

  .route-path {
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px;
    font-weight: 700;
    color: #38BDF8;
  }

  .route-target {
    font-size: 20px;
    font-weight: 700;
    color: #FF9900;
  }

  .route-detail {
    font-size: 18px;
    color: #94A3B8;
    margin-top: 4px;
  }

  /* Footer */
  .footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }

  .author {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 20px;
    font-weight: 600;
    color: #64748B;
  }

  .author-avatar {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #FF9900, #38BDF8);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #0B0F19;
    font-size: 18px;
  }

  .swipe-indicator {
    font-size: 20px;
    font-weight: 700;
    color: #FF9900;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .page-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    color: #64748B;
  }
</style>
</head>
<body>

  <!-- SLIDE 1: CAPA -->
  <div class="slide">
    <div>
      <div class="tag">☁️ AWS Architecture Essentials</div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <h1>Você sabe o que é <span class="highlight-orange">Behavior</span> na AWS?</h1>
      <p class="subtitle">Como desacoplar containers, economizar recursos na nuvem e acelerar a sua aplicação com <strong>Amazon CloudFront</strong>.</p>
    </div>
    <div class="footer">
      <div class="author">
        <div class="author-avatar">⚡</div>
        <span>AWS Insights Semanal</span>
      </div>
      <div class="swipe-indicator">Arraste para o lado ➔</div>
      <div class="page-num">1/5</div>
    </div>
  </div>

  <!-- SLIDE 2: O ERRO CLÁSSICO -->
  <div class="slide">
    <div>
      <div class="tag red">🛑 O Erro Clássico</div>
    </div>
    <div>
      <h1 style="font-size: 46px; margin-bottom: 28px;">Não queime <span class="highlight-orange">CPU cara</span> com arquivos estáticos!</h1>
      <div class="card-grid" style="margin-bottom: 24px;">
        <div class="card" style="border-top: 4px solid #38BDF8;">
          <div class="card-title" style="color: #38BDF8;">⚙️ Containers Docker</div>
          <div class="card-desc">Feitos para processar regras de negócio, APIs e banco de dados. Memória e CPU são os recursos mais caros da nuvem.</div>
        </div>
        <div class="card" style="border-top: 4px solid #F87171;">
          <div class="card-title" style="color: #F87171;">🖼️ Assets Estáticos</div>
          <div class="card-desc">Colocar fotos e bundles no Docker incha a imagem (1GB+) e consome conexões do servidor apenas lendo arquivos do disco.</div>
        </div>
      </div>
      <div class="card" style="background: rgba(56, 189, 248, 0.08); border-color: rgba(56, 189, 248, 0.25);">
        <p style="font-size: 21px; color: #E2E8F0;"><strong>💡 Regra de Ouro:</strong> Separe o poder computacional (Containers) do armazenamento e entrega de arquivos (S3 + Edge).</p>
      </div>
    </div>
    <div class="footer">
      <div class="author">
        <div class="author-avatar">⚡</div>
        <span>AWS Insights Semanal</span>
      </div>
      <div class="swipe-indicator">Arraste ➔</div>
      <div class="page-num">2/5</div>
    </div>
  </div>

  <!-- SLIDE 3: O CONCEITO -->
  <div class="slide">
    <div>
      <div class="tag blue">🚦 O Conceito</div>
    </div>
    <div>
      <h1 style="font-size: 46px; margin-bottom: 20px;">O que é o <span class="highlight-blue">CloudFront Behavior</span>?</h1>
      <p class="subtitle" style="margin-bottom: 32px;">É a regra de trânsito inteligente na Edge que avalia o caminho da URL e decide o destino de cada requisição.</p>
      
      <div style="display: flex; flex-direction: column; gap: 20px;">
        <div class="card" style="border-left: 6px solid #FF9900;">
          <div class="card-title" style="color: #FF9900;">1. Origem de Destino (Routing)</div>
          <div class="card-desc">Para onde enviar a rota? Bucket S3 (arquivos) ou Load Balancer / API Gateway (microsserviços)?</div>
        </div>
        <div class="card" style="border-left: 6px solid #38BDF8;">
          <div class="card-title" style="color: #38BDF8;">2. Política de Cache (TTL & Headers)</div>
          <div class="card-desc">Quanto tempo fica salvo nos pontos de presença da AWS? 1 ano para imagens ou Cache ZERO para rotas autenticadas?</div>
        </div>
      </div>
    </div>
    <div class="footer">
      <div class="author">
        <div class="author-avatar">⚡</div>
        <span>AWS Insights Semanal</span>
      </div>
      <div class="swipe-indicator">Arraste ➔</div>
      <div class="page-num">3/5</div>
    </div>
  </div>

  <!-- SLIDE 4: CENÁRIO REAL -->
  <div class="slide">
    <div>
      <div class="tag green">🛒 Cenário Real</div>
    </div>
    <div>
      <h1 style="font-size: 44px; margin-bottom: 24px;">Roteamento Inteligente em 1 Domínio</h1>
      
      <div class="route-item" style="border-left: 5px solid #34D399;">
        <div>
          <div class="route-path">/images/* & /static/*</div>
          <div class="route-detail">Cache de 1 ano (TTL longo) + Gzip/Brotli</div>
        </div>
        <div class="route-target">🪣 Amazon S3</div>
      </div>

      <div class="route-item" style="border-left: 5px solid #F87171;">
        <div>
          <div class="route-path">/api/checkout/*</div>
          <div class="route-detail">Cache ZERO | Repassa Auth, Cookies e POST/PUT</div>
        </div>
        <div class="route-target">⚖️ Container (ALB)</div>
      </div>

      <div class="route-item" style="border-left: 5px solid #38BDF8;">
        <div>
          <div class="route-path">Default (*)</div>
          <div class="route-detail">Entrega o index.html da Single Page App (SPA)</div>
        </div>
        <div class="route-target">🪣 Amazon S3</div>
      </div>
    </div>
    <div class="footer">
      <div class="author">
        <div class="author-avatar">⚡</div>
        <span>AWS Insights Semanal</span>
      </div>
      <div class="swipe-indicator">Arraste ➔</div>
      <div class="page-num">4/5</div>
    </div>
  </div>

  <!-- SLIDE 5: A PEGADINHA -->
  <div class="slide">
    <div>
      <div class="tag red">⚠️ Atenção Máxima</div>
    </div>
    <div>
      <h1 style="font-size: 44px; margin-bottom: 24px;">Cuidado com a <span class="highlight-orange">Ordem de Precedência</span>!</h1>
      
      <div class="card" style="margin-bottom: 24px; border: 1px solid rgba(255, 153, 0, 0.4);">
        <p style="font-size: 24px; font-weight: 700; color: #FF9900; margin-bottom: 12px;">Avaliação de CIMA para BAIXO ⬇️</p>
        <p class="card-desc">O CloudFront para na <strong>primeira regra</strong> compatível com o padrão da URL.</p>
        <p class="card-desc" style="margin-top: 8px;">Se você colocar o coringa <code style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 6px; color:#38BDF8;">*</code> no topo, ele engole todas as requisições e ignora as rotas de API e S3!</p>
      </div>

      <div class="card" style="background: rgba(52, 211, 153, 0.08); border-color: rgba(52, 211, 153, 0.3);">
        <p style="font-size: 22px; font-weight: 700; color: #34D399; margin-bottom: 6px;">📌 Salve este post!</p>
        <p style="font-size: 19px; color: #CBD5E1;">Deixe guardado para consultar quando for desenhar ou revisar sua próxima arquitetura na AWS.</p>
      </div>
    </div>
    <div class="footer">
      <div class="author">
        <div class="author-avatar">⚡</div>
        <span>AWS Insights Semanal</span>
      </div>
      <div style="font-size: 18px; font-weight: 700; color: #94A3B8;">Gostou? Comente e compartilhe! 🚀</div>
      <div class="page-num">5/5</div>
    </div>
  </div>

</body>
</html>
"""

def generate_pdf():
    html_path = "carousel.html"
    pdf_path = "carrossel_cloudfront_behaviors.pdf"
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    temp_profile = os.path.abspath("./.chrome_temp")
    os.makedirs(temp_profile, exist_ok=True)
    abs_html = os.path.abspath(html_path)
    abs_pdf = os.path.abspath(pdf_path)

    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={temp_profile}",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={abs_pdf}",
        f"file://{abs_html}"
    ]
    
    print(f"Gerando PDF com Chrome headless...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(pdf_path):
        print(f"Sucesso! Arquivo criado: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    else:
        print(f"Erro ao gerar: {result.stderr}")

if __name__ == "__main__":
    generate_pdf()
