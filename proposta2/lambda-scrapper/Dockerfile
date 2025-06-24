# Exemplo para Python/Selenium no Lambda
FROM public.ecr.aws/lambda/python:3.9

# Instalar dependências do sistema para Chrome/Chromedriver
# Adaptado para sistemas baseados em Debian/Ubuntu, se for RedHat/CentOS use yum
RUN apt-get update && apt-get install -yq unzip libgomp
# Download e instalação do ChromeDriver e Chrome (adapte as versões se necessário)
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)     && wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip -O /tmp/chromedriver_linux64.zip     && unzip /tmp/chromedriver_linux64.zip -d /usr/bin/     && rm /tmp/chromedriver_linux64.zip     && chmod +x /usr/bin/chromedriver

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -fy
RUN rm google-chrome-stable_current_amd64.deb

# Copiar o código do scrapper e instalar dependências Python
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY scrapper.py ./

# Definir o handler da Lambda
CMD [ "scrapper.lambda_handler" ]
