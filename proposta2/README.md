# Proposta 2: Avaliação e Melhoria de Sistema de Scrapping

---

## 💡 Cenário Atual e Análise Crítica

O cenário hipotético apresenta um sistema de scrapping que, ao detectar um bloqueio de IP por parte do site alvo, reage provisionando uma **nova instância Lambda** com um novo IP público. Embora a intenção seja contornar o bloqueio, essa abordagem introduz graves problemas:

* **Custo Elevado:** Provisionar e desativar Lambdas repetidamente é ineficiente e caro. Cada nova invocação pode incorrer em custos adicionais de provisionamento e latência.
* **Inoperabilidade e Latência:** A cada bloqueio, há um atraso significativo para provisionar uma nova Lambda, causando inoperabilidade no processo de scrapping e perda de performance.
* **Complexidade e Manutenção:** A lógica de provisionamento de infraestrutura (Terraform) fica acoplada à lógica de negócio (o scrapper), dificultando a manutenção e a reutilização.
* **Escalabilidade Limitada:** A dependência do provisionamento dinâmico de Lambdas para cada bloqueio impede uma escalabilidade horizontal eficiente para lidar com grandes volumes de scrapping.
* **Anti-padrão de Lambda "Gorda":** A Lambda está assumindo responsabilidades demais (scrapping E gerenciamento de IP), o que vai contra o princípio de funções serverless serem pequenas e focadas.

---

## 🏛��� Nova Arquitetura Proposta (Otimizada)

A solução proposta visa desacoplar a lógica de contorno de IP do processo de scrapping, utilizando serviços gerenciados da AWS para maior eficiência, recursividade, performance e escalabilidade, com um foco significativo na **redução de custos**.

![Diagrama de Arquitetura Scrapping Otimizado](../diagrams/arquitetura_proposta2.png)

### Componentes Chave:

* **Scheduler / Trigger (Ex: EventBridge + Lambda):** Inicia o processo, colocando URLs ou tarefas de scrapping em uma fila SQS em intervalos definidos ou em resposta a eventos.
* **Amazon SQS (Simple Queue Service):**
    * **Fila de Tarefas (Main Queue):** Atua como um buffer para as URLs/tarefas de scrapping. As Lambdas worker puxam tarefas daqui.
    * **Fila de Re-tentativas / DLQ (Dead-Letter Queue):** Mensagens que falham devido a bloqueios de IP ou outros erros transitórios são reenviadas para esta fila com um atraso, permitindo que um IP diferente (do pool de proxies) seja tentado na próxima vez. Mensagens com falhas persistentes vão para uma DLQ final para análise.
* **AWS Lambda Workers (Pool de Lambdas):**
    * Múltiplas funções Lambda de curta duração configuradas para ler mensagens da fila SQS.
    * Cada Lambda invoca o código do scrapper (empacotado em uma imagem Docker).
    * Um **pool** de Lambdas é criado, e a AWS gerencia a escalabilidade horizontal desse pool automaticamente com base na demanda da fila SQS.
* **Serviço de Proxy Rotativo:**
    * Um serviço externo ou interno (ex: um pool de NAT Gateways, um cluster Nginx/Squid atrás de um ALB, ou um provedor de IPs residenciais/datacenter de terceiros) que fornece IPs dinâmicos e rotativos.
    * As Lambdas worker enviam suas requisições HTTP através deste serviço de proxy.
    * **Crucial:** O scrapper não tenta mudar seu próprio IP; ele apenas usa o proxy, que se encarrega da rotação.
* **Amazon S3 (Simple Storage Service):** Bucket para armazenar os dados raspados. Alta durabilidade, escalabilidade e custo-benefício.
* **Amazon CloudWatch:** Para monitoramento de logs (CloudWatch Logs) e métricas (CloudWatch Metrics) de todas as Lambdas e filas SQS, essencial para observabilidade e alertas.

---

## 🔄 Fluxo de Operação Otimizado

1.  **Início da Tarefa:** O Scheduler coloca uma mensagem (contendo a URL a ser raspada e metadados da tarefa) na **SQS Queue de Tarefas**.
2.  **Processamento pela Lambda:** Uma **Lambda Worker** é invocada automaticamente pela AWS ao detectar mensagens na fila.
3.  **Execução do Scrapper:** O código Python dentro da Lambda (rodando na imagem Docker) utiliza o **Serviço de Proxy Rotativo** para fazer a requisição HTTP ao site alvo.
4.  **Detecção de Bloqueio/Erro:**
    * Se o scrapper for bem-sucedido, os dados são salvos no **S3**. A mensagem é automaticamente removida da fila pela Lambda.
    * Se o scrapper detectar um bloqueio de IP (código de status 403/429, ou padrão específico na resposta), a **mesma tarefa é reenviada para a SQS Queue de Re-tentativas** com um `DelaySeconds`.
5.  **Re-tentativa:** Após o atraso, a mensagem da fila de re-tentativas é reprocessada por outra Lambda Worker. Devido à rotação de IPs no serviço de proxy, há uma grande chance de que um IP diferente seja usado, contornando o bloqueio anterior.
6.  **DLQ:** Se uma mensagem exceder um número máximo de re-tentativas (configurado na fila SQS), ela é enviada para uma Dead-Letter Queue (DLQ) para análise manual e depuração, evitando que bloqueie a fila principal.

---

## ✅ Ganhos e Benefícios da Nova Arquitetura

### 1. Performance Otimizada:

* **Paralelismo Natural:** Múltiplas Lambdas podem processar tarefas da SQS simultaneamente, acelerando o processo de scrapping.
* **Re-tentativas com Backoff:** A fila SQS com `DelaySeconds` evita ataques de "martelo" em IPs bloqueados e permite que o proxy rotativo troque de IP antes da próxima tentativa.
* **Gerenciamento de Dependências:** O empacotamento em Docker garante que todas as dependências (Selenium, Chromedriver, etc.) estejam pré-configuradas e prontas para uso, reduzindo o tempo de inicialização da Lambda.

### 2. Recursividade (Resiliência a Bloqueios):

* **Desacoplamento:** A lógica de contorno de IP é abstraída para o Serviço de Proxy Rotativo. A Lambda não precisa saber sobre a gestão de IPs.
* **Re-tentativas Automaticas:** O SQS gerencia as re-tentativas de forma nativa e resiliente.
* **Pool de IPs:** O serviço de proxy garante que um novo IP seja tentado a cada re-tentativa, aumentando a probabilidade de sucesso.

### 3. Redução de Custos:

* **Pagamento por Uso (Serverless):** Com Lambdas e SQS, você paga apenas pelo tempo de execução e mensagens processadas, não por instâncias ociosas.
* **Sem Provisionamento Manual:** Elimina a necessidade de provisionar/desprovisionar Lambdas via Terraform a cada bloqueio, reduzindo a sobrecarga e o custo operacional.
* **Uso Eficiente de IPs:** O proxy rotativo otimiza o uso de IPs, o que pode ser mais econômico do que ter IPs estáticos ou múltiplos NATs por VPC.

### 4. Maior Escalabilidade:

* **Escalabilidade Automática da Lambda:** A AWS gerencia o pool de Lambdas workers, escalando-o automaticamente para cima e para baixo com base no volume de mensagens na SQS.
* **SQS Escalável:** O SQS é um serviço de fila altamente escalável, capaz de lidar com milhões de mensagens.
* **S3 para Armazenamento:** Oferece armazenamento ilimitado e altamente escalável para os dados raspados.

---

### 🧪 Validação Local com Docker

O componente `proposta2/lambda-scrapper/` foi projetado para ser empacotado como uma imagem Docker, que é a forma como a AWS Lambda opera funções containerizadas. É possível construir e executar esta imagem Docker localmente para validar a lógica do scrapper e suas dependências.

**Para construir a imagem:**
```bash
docker build -t meu-scrapper-lambda ./proposta2/lambda-scrapper
```

**Para simular uma invocação Lambda localmente (com um `event.json` na mesma pasta):**
```bash
docker run -it --rm -v "$(pwd)/event.json:/var/task/event.json" meu-scrapper-lambda:latest lambda_handler event.json
```
_Nota: A execução local simulará o fluxo, mas não interage com serviços AWS reais (SQS/S3) a menos que configurado com ferramentas como LocalStack._

---
