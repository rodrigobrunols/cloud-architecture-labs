# 🚀 Script de Publicação no LinkedIn - Lab 01

Este guia contém o passo a passo exato, o texto pronto para publicação e o primeiro comentário para o post da semana sobre **AWS CloudFront Behaviors**.

---

## 📋 Informações Gerais do Post

* **Tema:** Desacoplando Containers Docker e Otimizando Custos com AWS CloudFront Behaviors.
* **Formato:** Publicação com Anexo de Documento (Carrossel PDF).
* **Arquivo a Anexar:** [`carrossel_cloudfront_behaviors.pdf`](./carrossel_cloudfront_behaviors.pdf)
* **Título do Documento no LinkedIn:** `Desacoplando Containers com AWS CloudFront Behaviors`
* **Melhores Dias para Publicar:** Terça, Quarta ou Quinta-feira.
* **Melhores Horários:** 08:00 às 09:00 ou 12:00 às 13:15.

---

## 📄 Texto do Post (Copiar e Colar)

```text
Se alguém te perguntar hoje: "Você sabe o que é Behavior na AWS?", o que você responderia? 🤔

Na primeira vez que ouvi esse termo isolado, pensei em psicologia, design patterns, comportamento humano... Mas não: é um dos recursos mais poderosos do Amazon CloudFront. 😂

E ele resolve um dos erros mais comuns de arquitetura: colocar arquivos estáticos dentro de containers Docker.

Containers devem ser leves e focados em lógica de negócio (CPU e memória RAM custam caro na nuvem!). Se o seu backend em Node, Go ou Java tiver que gastar threads servindo imagens de 5MB, você está queimando dinheiro à toa.

É aí que o CloudFront entra para separar o jogo no mesmo domínio:

🖼️ /images/* e /static/* ➔ Bucket S3
→ Regra: Cache agressivo (TTL longo). O S3 entrega os arquivos na borda, a imagem Docker cai de 1.5GB para 100MB e seu backend nem sente o tráfego.

💳 /api/checkout/* e /api/carrinho/* ➔ Container (ALB/ECS)
→ Regra: ZERO cache! O CloudFront repassa requisições POST/PUT, cookies e autenticação direto pro backend processar a regra de negócio.

🏠 Default (*) ➔ S3 com SPA (index.html)
→ Entrega o front-end React/Vue desacoplado da API.

💡 A pegadinha de ouro:
O CloudFront avalia as regras de CIMA para BAIXO (ordem de precedência). Se colocar o coringa (*) no topo, ele engole tudo e ignora as regras do S3!

Confira os detalhes no carrossel acima! 👆

E por aí: na arquitetura de vocês os assets já ficam no S3/CDN ou ainda rodam dentro do container? Me conta nos comentários! 👇

Código Terraform completo e diagrama de arquitetura no primeiro comentário! 💻👇

#AWS #CloudArchitecture #DevOps #Docker #WebDevelopment #SystemDesign #Terraform #CloudFront
```

---

## 💬 Primeiro Comentário (Postar Imediatamente após Publicar)

```text
💻 O código Terraform completo deste lab, com a configuração de Origin Access Control (OAC), políticas de cache e o diagrama de arquitetura, já está disponível no GitHub:

👉 https://github.com/rodrigobrunols/cloud-architecture-labs/tree/main/01-cloudfront-behaviors

Fiquem à vontade para clonar, testar e sugerir melhorias! 🚀
```

---

## 💡 Estratégia de Mídia & Código

1. **Por que não colar 200 linhas de Terraform no corpo do post?**
   O LinkedIn quebra a indentação e reduz o engajamento visual. Os destaques em código já aparecem no carrossel PDF na janela de terminal estilo macOS.
2. **Por que o link fica no primeiro comentário?**
   O algoritmo do LinkedIn penaliza publicações que colocam links externos no texto principal, reduzindo o alcance orgânico em até 50%. Deixar o link no comentário preserva o alcance máximo.
