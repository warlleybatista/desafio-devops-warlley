import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import boto3

# Variáveis de ambiente (serão injetadas pela AWS Lambda ou para teste local)
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL_FOR_RETRIES', 'http://localhost:4566/000000000000/my-retry-queue') # Exemplo para LocalStack
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'my-scrapped-data-bucket')
PROXY_SERVICE_ENDPOINT = os.environ.get('PROXY_SERVICE_ENDPOINT', 'http://your-proxy-service-url.com')

# Clientes AWS (para ambiente real, Lambda usa roles, para local pode precisar de configuração)
sqs_client = boto3.client('sqs')
s3_client = boto3.client('s3')

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrap_url(url, task_data):
    driver = None
    try:
        print(f"Tentando raspar: {url} (Task ID: {task_data.get('task_id')})")

        # Exemplo com requests e proxy (mais comum para rotação de IP em larga escala)
        proxies = {'http': PROXY_SERVICE_ENDPOINT, 'https': PROXY_SERVICE_ENDPOINT}
        response = requests.get(url, proxies=proxies, timeout=30)
        if response.status_code in [403, 429]: # Códigos comuns para bloqueio/rate limit
           raise Exception("IP_BLOCKED_OR_RATE_LIMITED")
        content = response.text

        # OU com Selenium se for necessário JavaScript (descomente e adapte)
        # driver = get_chrome_driver()
        # driver.get(url)
        # content = driver.page_source

        # Simula salvamento no S3
        print(f"Simulando salvamento de dados para {url} no S3: {S3_BUCKET_NAME}/scrapped_data/{task_data.get('task_id')}.html")
        # s3_client.put_object(
        #     Bucket=S3_BUCKET_NAME,
        #     Key=f"scrapped_data/{task_data.get('task_id')}-{os.urandom(4).hex()}.html",
        #     Body=content
        # )
        print(f"Dados de {url} processados com sucesso.")
        return True

    except Exception as e:
        error_message = str(e)
        print(f"Erro ao raspar {url}: {error_message}")

        if "IP_BLOCKED_OR_RATE_LIMITED" in error_message or "403" in error_message or "429" in error_message:
            print(f"Bloqueio de IP detectado para {url}. Reenviando tarefa para fila de re-tentativas.")
            # Simula reenviar para SQS
            # sqs_client.send_message(
            #     QueueUrl=SQS_QUEUE_URL,
            #     MessageBody=json.dumps(task_data),
            #     DelaySeconds=30
            # )
            print("Tarefa simuladamente reenviada para fila de re-tentativas.")
        else:
            print(f"Erro inesperado: {error_message}. Não reenviando para fila de re-tentativa.")
        return False
    finally:
        if driver:
            driver.quit()

def lambda_handler(event, context):
    print(f"Evento recebido: {json.dumps(event)}")
    for record in event.get('Records', []):
        try:
            message_body = json.loads(record['body'])
            url_to_scrap = message_body.get('url')
            task_id = message_body.get('task_id', 'no-id')

            if url_to_scrap:
                scrap_url(url_to_scrap, message_body)
            else:
                print(f"Mensagem SQS inválida: {message_body}")
        except Exception as e:
            print(f"Erro ao processar record: {e} - Record: {record}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processamento de mensagens SQS concluído.')
    }

# Para testes locais com Docker, o 'event.json' é montado e lido.
# Não é necessário o bloco __main__ para a execução via CMD no Dockerfile Lambda.
# O Dockerfile Lambda executa 'lambda_handler event.json'
