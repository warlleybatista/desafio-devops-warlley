# Proposta 1: CI/CD com Jenkins e GitOps para Zero Downtime



###  Visão Geral da Solução ###

Esta proposta detalha a implementação de um pipeline de Integração Contínua (CI) e Entrega Contínua (CD) utilizando "Jenkins" para orquestração, "Argo CD" para um fluxo de "GitOps", e "Kubernetes (Amazon EKS)" como plataforma de deploy. O objetivo principal é garantir "deploys sem inoperabilidade (zero downtime)", alta performance, segurança, disponibilidade e escalabilidade, enquanto otimiza os custos.

A estratégia centra-se no conceito de "GitOps", onde o repositório Git se torna a única fonte de verdade para a configuração da aplicação e da infraestrutura.



### Arquitetura Proposta ###

A seguir, apresentamos o diagrama de arquitetura que ilustra o fluxo completo do desenvolvimento à produção.

![image](https://github.com/user-attachments/assets/62ea99d3-a563-45d3-9d09-2278c8073933)




### Componentes Chave:

* Desenvolvedor: Inicia o processo com um commit de código.
* GitHub (ou outro SCM): Hospeda o código-fonte da aplicação e, crucialmente, os manifestos Kubernetes (configurações do deploy) em um repositório GitOps separado.
* Jenkins:
    * Orquestrador da pipeline de CI/CD.
    * Executa pipelines baseadas em \`Jenkinsfile\` (Pipeline as Code).
    * Configurado para rodar seus "agentes em Pods dinâmicos no Kubernetes" para escalabilidade e isolamento.
* Amazon ECR (Elastic Container Registry): Serviço de registro de imagens Docker seguro e gerenciado pela AWS, onde as imagens da aplicação são armazenadas após o build.
* Amazon EKS (Elastic Kubernetes Service): Serviço gerenciado de Kubernetes da AWS, onde as aplicações são orquestradas e executadas. Proporciona alta disponibilidade, escalabilidade e resiliência.
* Argo CD:
    * Ferramenta de "GitOps" que opera dentro do EKS.
    * Monitora continuamente o repositório GitOps de manifestos.
    * Detecta automaticamente mudanças nos manifestos e sincroniza o estado desejado com o estado real do cluster Kubernetes.
    * Fornece visibilidade do estado do deploy e facilita rollbacks.
* Application Load Balancer / Proxy Reverso:
    * Atua como o ponto de entrada para o tráfego da aplicação.
    * Gerencia o tráfego de entrada e distribui para as instâncias da aplicação em execução no EKS.
    * Essencial para o "zero downtime" ao gerenciar o tráfego durante o Rolling Update.



### Fluxo da Pipeline (Homologação e Produção)

A pipeline é definida como código no "Jenkinsfile" e opera da seguinte forma:

1.  Commit do Código (CI):
    * Um desenvolvedor faz um push de novas alterações de código para o repositório da aplicação (ex: "main" ou um branch de feature).

2.  Trigger da Pipeline no Jenkins:
    * O Jenkins detecta a mudança no repositório de código e inicia automaticamente a pipeline de CI/CD.

3.  Build e Testes:
    * Um Jenkins Agent (executando em um Pod Kubernetes dinâmico) clona o repositório.
    * O código da aplicação é compilado e os testes unitários/de integração são executados para garantir a qualidade.
    * Exemplo no "Jenkinsfile" (jenkins/Jenkinsfile).

4.  Construção e Push da Imagem Docker:
    * Com base no "Dockerfile" da aplicação, uma nova imagem Docker é construída.
    * Essa imagem é tagueada (ex: \`v<BUILD_NUMBER>\`) e enviada para o Amazon ECR.
    * Exemplo no "Dockerfile" (app-code/Dockerfile).

5.  Atualização do Repositório GitOps (CD para Homologação):
    * Ponto crucial do GitOps: O Jenkins não faz o deploy diretamente no Kubernetes. Em vez disso, ele atualiza a tag da imagem no arquivo de manifesto Kubernetes (ex: \`minha-app-homolog.yaml\`) dentro do repositório GitOps de manifests.
    * Esta alteração (um novo commit com a nova tag da imagem) é então enviada para o branch de homologação "homolog" do repositório de manifests.
    * Veja como a atualização do manifest é orquestrada no "Jenkinsfile" (jenkins/Jenkinsfile).

6.  Sincronização e Deploy do Argo CD:
    * O Argo CD, que está continuamente monitorando o branch "homolog" do repositório de manifests, detecta a nova tag da imagem.
    * Ele puxa as mudanças e inicia automaticamente o processo de sincronização/deploy no cluster EKS.
    * O Kubernetes executa uma estratégia de Rolling Update, substituindo gradualmente os pods antigos pelos novos, sem interromper o serviço.
    * Exemplo de manifesto Kubernetes (kubernetes/minha-app-homolog.yaml).

7.  Aprovação Manual para Produção:
    * Após o sucesso do deploy em homologação e a validação, a pipeline do Jenkins inclui um estágio de aprovação manual.
    * Com a aprovação, o processo de deploy se estende para o ambiente de produção.

8.  Atualização do Repositório GitOps (CD para Produção):
    * Similar ao passo 5, o Jenkins atualiza o manifesto de produção (ex: minha-app-prod.yaml) no branch "main" do repositório GitOps.

9.  Deploy em Produção via Argo CD:
    * O Argo CD detecta a mudança no branch "main" e sincroniza o deploy da nova versão da aplicação no ambiente de produção do EKS, também utilizando Rolling Update.

---

### Justificativas e Benefícios da Solução

### 1. Zero Downtime:

* Rolling Update no Kubernetes: As novas versões da aplicação são introduzidas gradualmente, enquanto as versões antigas são desativadas. O tráfego é roteado para os novos pods apenas após eles estarem saudáveis.
* Application Load Balancer / Proxy Reverso: O Load Blancer monitora a saúde dos pods e direciona o tráfego apenas para os pods saudáveis (versão antiga ou nova), garantindo que o usuário final nunca seja impactado durante a transição.

### 2. Performance:

* Jenkins Agents em Kubernetes: Os agentes de build são provisionados sob demanda como Pods no EKS, escalando horizontalmente para atender à demanda da pipeline e liberando recursos quando ociosos.
* Containers Leves: O uso de imagens Docker otimiza o empacotamento e a inicialização da aplicação.
* Kubernetes (EKS): O EKS oferece orquestração eficiente, balanceamento de carga interna e escalabilidade automática de pods, garantindo que a aplicação sempre tenha recursos adequados.

### 3. Segurança:

* GitOps: O repositório Git se torna a única fonte de verdade auditável. Todas as mudanças na configuração são versionadas e rastreáveis.
* IAM Roles (AWS): Permissões granulares são aplicadas via AWS IAM para Jenkins, ECR, EKS e outras interações AWS.
* Segregação de Ambientes: Ambientes de homologação e produção são isolados, minimizando o risco de impacto entre eles.
* ECR (Segurança de Imagens): Imagens Docker são armazenadas em um registro seguro com controle de acesso.

### 4. Disponibilidade:

* Alta Disponibilidade do EKS: O Kubernetes é internamente projetado para alta disponibilidade, com réplicas de pods, balanceamento de carga e detecção automática de falhas.
* Alta Disponibilidade do Jenkins: O Jenkins pode ser configurado em HA (Master/Agent ou Kubernetes Plugin) para evitar um único ponto de falha.
* Argo CD em Alta Disponibilidade: Pode ser implantado com réplicas para garantir sua própria disponibilidade.

### 5. Escalabilidade:

* Escalabilidade Horizontal do EKS: O Kubernetes pode escalar automaticamente o número de pods da aplicação com base na carga, garantindo que a aplicação suporte picos de tráfego.
* Escalabilidade dos Jenkins Agents: Agentes sob demanda no EKS permitem que o Jenkins lide com múltiplos builds simultaneamente sem gargalos.
* ECR: Escalável para armazenar um grande volume de imagens.

### 6. Otimização de Custos:

* Jenkins Agents Dinâmicos: Pagamento por recursos apenas quando usados, em vez de servidores Jenkins fixos e superprovisionados.
* EKS (Gerenciado): Reduz o esforço operacional de gerenciar o cluster Kubernetes em comparação com uma configuração auto-gerenciada.
* ALB: Custo-benefício para balanceamento de carga em comparação com outras soluções.

---

### Como Executar e Testar esta Proposta Localmente (Simulação)

Esta proposta foca na arquitetura e automação de CI/CD. A execução completa em um ambiente real requer infraestrutura AWS e um cluster Kubernetes. No entanto, você pode simular partes do processo ou preparar o ambiente para um deploy futuro.

### Pré-requisitos Específicos

* Docker e Docker Compose (já mencionados no README principal).
* Minikube ou Kind: Para simular um cluster Kubernetes localmente.
    * [Instalar Minikube](https://minikube.sigs.k8s.io/docs/start/)
    * [Instalar Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

### Passos de Simulação / Preparação

1.  Navegue para a pasta da Proposta 1:
    ```bash
    cd ../proposta1
    ```
2.  Construa a imagem Docker da aplicação (exemplo):
    ```bash
    docker build -t minha-app-exemplo:latest .
    ```
3.  Simule a execução do Jenkins (com Docker Compose):
    * Se você tiver um `docker-compose.yml` para subir o Jenkins localmente:
        ```bash
        docker-compose up -d
        ```
    * Acesse o Jenkins em `http://localhost:8080` e configure a pipeline usando o `Jenkinsfile` fornecido.
4.  Simule o deploy no Kubernetes (com Minikube/Kind):
    * Se você tiver um cluster local configurado:
        ```bash
        kubectl apply -f k8s-manifests/
        ```
    * (verificar o deploy, ex: `kubectl get pods`, `kubectl get svc`)

