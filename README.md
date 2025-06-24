# Desafio Vaga DevOps

---

## 🚀 Visão Geral do Projeto

Este repositório apresenta as soluções propostas para o Desafio DevOps, abordando dois cenários principais, focando em arquitetura, design e a justificativa das escolhas técnicas:

1.  **Implementação de CI/CD com Jenkins e GitOps:** Uma solução de entrega contínua projetada para deploy de aplicações com zero downtime, alta performance, segurança e escalabilidade.
2.  **Avaliação e Melhoria de Sistema de Scrapping:** Análise crítica de uma arquitetura de scrapping existente e proposta de uma solução otimizada para lidar com bloqueios de IP, custos e escalabilidade.

---

## 📁 Estrutura do Repositório

O projeto está organizado nas seguintes pastas para facilitar a navegação e compreensão das propostas:

* **`proposta1/`**: Contém a documentação detalhada e exemplos de código relacionados à solução de CI/CD.
    * `proposta1/app-code/`: Exemplo de código de uma aplicação web simples com seu `Dockerfile`.
    * `proposta1/jenkins/`: `Jenkinsfile` de exemplo ilustrando o pipeline de CI/CD.
    * `proposta1/kubernetes/`: Manifestos Kubernetes (`.yaml`) de exemplo para deploy.
* **`proposta2/`**: Abriga a documentação e exemplos de código para a solução otimizada de scrapping.
    * `proposta2/lambda-scrapper/`: Pseudocódigo Python para a função Lambda scrapper, `Dockerfile` e `requirements.txt`.
    * `proposta2/terraform/`: Exemplo de código Terraform para provisionar os recursos AWS da solução.
* **`diagrams/`**: Armazena os diagramas de arquitetura visual para ambas as propostas.

---

## 🎯 Proposta 1: CI/CD com Jenkins e GitOps para Zero Downtime

Nesta seção, detalhamos a concepção de uma pipeline de CI/CD robusta, utilizando Jenkins para orquestração e Argo CD para um deploy GitOps em um cluster Kubernetes (EKS). O foco é garantir a entrega contínua de aplicações com mínima ou nenhuma interrupção, alta performance e escalabilidade, enquanto se mantém a segurança e a otimização de custos.

**Para explorar a arquitetura, o fluxo de trabalho detalhado, as justificativas técnicas e os exemplos de código, acesse a documentação completa:**

➡��� **[Detalhes da Proposta 1](proposta1/README.md)**

---

## 🕸��� Proposta 2: Avaliação e Melhoria de Sistema de Scrapping

Esta seção apresenta uma análise da infraestrutura de scrapping atual e propõe uma nova arquitetura para superar desafios como bloqueio de IP, ineficiência de custos e escalabilidade limitada. A solução otimizada visa uma execução mais resiliente, performática e econômica.

**Para entender a análise crítica, a nova arquitetura proposta, os ganhos esperados e os exemplos de código, confira a documentação detalhada:**

➡��� **[Detalhes da Proposta 2](proposta2/README.md)**

---

## 🛠��� Tecnologias Envolvidas

As principais tecnologias e conceitos empregados na concepção das soluções incluem:

* **Versionamento:** Git, GitHub
* **CI/CD:** Jenkins, Argo CD, Pipelines como Código
* **Conteinerização:** Docker
* **Orquestração de Containers:** Kubernetes (Amazon EKS)
* **Infraestrutura como Código (IaC):** Terraform
* **Serviços Cloud (AWS):** AWS Lambda, Amazon SQS, Amazon S3, Amazon ECR, Amazon ALB (Application Load Balancer)
* **Linguagens de Script:** Groovy (para Jenkinsfile), Python (para lógica de scrapping na Lambda)
* **Diagramação:** Ferramentas de design de arquitetura (ex: Visual Paradigm Online)

---
