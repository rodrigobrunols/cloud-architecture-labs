# 🚀 Script de Publicação no LinkedIn - Lab 02

Este guia contém o passo a passo exato, o texto pronto para publicação e o primeiro comentário para o post da semana sobre **Estratégias de Invalidação de Cache no Amazon CloudFront & Pipelines CI/CD**.

---

## 📋 Informações Gerais do Post

* **Tema:** Invalidação de Cache Cirúrgica no Amazon CloudFront e Boas Práticas em Pipelines CI/CD.
* **Formato:** Publicação com Anexo de Documento (Carrossel PDF).
* **Arquivo a Anexar:** [`carrossel_cloudfront_cache_invalidation.pdf`](./carrossel_cloudfront_cache_invalidation.pdf)
* **Título do Documento no LinkedIn:** `Invalidação de Cache no CloudFront Sem Quebrar Produção`
* **Melhores Dias para Publicar:** Terça, Quarta ou Quinta-feira.
* **Melhores Horários:** 08:00 às 09:00 ou 12:00 às 13:15.

---

## 📄 Texto do Post (Copiar e Colar)

```text
Phil Karlton já profetizava nos anos 90:
"Só existem duas coisas difíceis na Ciência da Computação: invalidação de cache e dar nome às coisas." 😂
(E para alguns, os erros de off-by-one!).

Se você usa Amazon CloudFront com React/Vue no frontend, aposto que a tentação de resolver a primeira dor rodando um `aws cloudfront create-invalidation --paths "/*"` a cada deploy já passou pelo seu pipeline. 🚨

Parece o caminho da paz: "Vou purgar tudo para garantir que o cliente veja o botão novo".
Mas na prática, o que acontece 2 segundos após o deploy é um filme de terror:

💥 O Cache Hit Ratio da CDN vai direto pro chão: 0%.
💥 Efeito Manada: Milhares de usuários vão buscar arquivos pesados no S3 e no backend ao mesmo tempo (e o alarme de CPU começa a chorar).
💥 A temida Tela Branca (404): O usuário que estava no meio da compra clica em "pagar" e o navegador dele tenta baixar um chunk JS antigo que seu deploy acabou de explodir do cache.

Como resolver isso com classe e manter a paz na Black Friday?
A regra de ouro é: Cache-Busting (Fingerprinting) > Invalidation.

A estratégia dos 3 pilares resolve sem sustos:

📦 1. Bundles com Hash (/assets/app.a8f9.js, style.12b3.css)
➔ Cache-Control: `public, max-age=31536000, immutable`
→ Fica 1 ano na Edge. NUNCA invalide! O Vite/Webpack já mudou o nome do arquivo pra você.

🏠 2. Entrypoint SPA (index.html)
➔ Cache-Control: `public, max-age=0, must-revalidate`
→ O navegador sempre checa se há versão nova. Aqui sim entra a cirurgia: invalide APENAS `/index.html` e `/`.

⚙️ 3. Backend APIs (/api/*)
➔ Carrinho/Auth: `no-store` (Zero cache, dados frescos).
➔ Catálogo: `s-maxage=60, stale-while-revalidate=300` (Aguenta tráfego pesado rindo).

🚀 O Segredo no Pipeline CI/CD (GitHub Actions / GitLab):
• 1º: Suba os novos chunks JS/CSS no S3 (excluindo o index.html).
• 2º: Suba o index.html por último.
• 3º: Invalide CIRURGICAMENTE apenas `/index.html`.

Zero telas brancas, propagação imediata e você nunca queima os 1.000 caminhos grátis da AWS! 💰

Confira o passo a passo visual e o fluxo de CI/CD no carrossel acima! 👆

E por aí: você já passou pelo momento "tela branca pós-deploy" ou o seu pipeline já faz invalidação cirúrgica? Me conta nos comentários! 👇

Código Terraform e pipeline CI/CD completo no primeiro comentário! 💻👇

#AWS #CloudArchitecture #DevOps #CICD #React #CloudFront #SystemDesign #Terraform #SoftwareEngineering
```

---

## 💬 Primeiro Comentário (Postar Imediatamente após Publicar)

```text
💻 O código Terraform completo deste lab, com a configuração de Origin Access Control (OAC), políticas de cache cirúrgicas e exemplo de pipeline CI/CD com menor privilégio, já está disponível no GitHub:

👉 https://github.com/rodrigobrunols/cloud-architecture-labs/tree/main/02-cloudfront-cache-invalidation

Fiquem à vontade para clonar, testar e sugerir melhorias! 🚀
```

---

## 💡 Estratégia de Mídia & Código

1. **Por que a citação de Phil Karlton funciona tão bem?**
   É uma das referências mais clássicas e reconhecidas da computação. Cria identificação e conexão imediata com engenheiros de software, arquitetos e DevOps logo nas primeiras duas linhas (antes do botão *"...ver mais"*).
2. **Por que não invalidar `/*` no CI/CD?**
   Além de degradar a performance da aplicação no momento do deploy, a AWS cobra \$0,005 por caminho de invalidação adicional após as primeiras 1.000 requisições gratuitas no mês.
3. **Por que o link fica no primeiro comentário?**
   O algoritmo do LinkedIn penaliza publicações com links externos no corpo do post, reduzindo o alcance orgânico em até 50%. A recomendação é manter o link sempre no primeiro comentário.
