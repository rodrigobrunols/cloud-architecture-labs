# ☁️ Cloud Architecture Labs & Weekly Insights

[![AWS Architecture](https://img.shields.io/badge/AWS-Architecture-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rodrigo_Bruno-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rodrigobrunols)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

Este repositório reúne implementações práticas, diagramas e códigos de **Infraestrutura como Código (Terraform)** que acompanham minha série semanal de publicações sobre **Arquitetura Cloud e AWS no LinkedIn**.

O objetivo principal é transformar conceitos de alta disponibilidade, escalabilidade, desacoplamento e otimização de custos em **código limpo, modular e pronto para teste**.

---

## 📚 Índice de Labs Semanais

| Lab | Tópico Principal | Serviços AWS | Código / Lab | Carrossel PDF |
| :---: | :--- | :--- | :---: | :---: |
| **#01** | **Roteamento Inteligente na Edge com CloudFront Behaviors** | CloudFront, S3, ALB, OAC | [Acessar Lab](./01-cloudfront-behaviors) | [Baixar PDF](./01-cloudfront-behaviors/carrossel_cloudfront_behaviors.pdf) |
| **#02** | *Em breve...* | — | — | — |

---

## 🛠️ Tecnologias & Ferramentas
* **Cloud Provider:** Amazon Web Services (AWS)
* **Infraestrutura como Código (IaC):** Terraform / OpenTofu
* **Padrões de Arquitetura:** Edge Routing, Desacoplamento de Containers, Caching Strategy, Zero-Trust (OAC), Multi-Origin.

---

## 🚀 Como Executar os Exemplos

Cada lab é isolado e possui seu próprio diretório contendo documentação, diagramas e arquivos Terraform:

```bash
# 1. Clone o repositório
git clone https://github.com/rodrigobrunols/cloud-architecture-labs.git

# 2. Acesse o lab desejado
cd cloud-architecture-labs/01-cloudfront-behaviors

# 3. Inicialize o Terraform e visualize o plano
terraform init
terraform plan
```

---

## 🤝 Conecte-se comigo
Acompanhe os próximos artigos e participe das discussões técnicas:
* **LinkedIn:** [linkedin.com/in/rodrigobrunols](https://linkedin.com/in/rodrigobrunols)
* **GitHub:** [@rodrigobrunols](https://github.com/rodrigobrunols)

---
*Distribuído sob a licença MIT. Sinta-se livre para usar, clonar e adaptar os modelos de arquitetura nos seus próprios projetos.*
