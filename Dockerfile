FROM python:3.8-alpine3.12

COPY src/ /src/
COPY res/ /res/
COPY var/ /var/

RUN pip3 install -r /res/requirements.txt

# Download and install Chromedriver
# RUN wget "http://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip" && \
#     unzip chromedriver_linux64.zip -d /res/ && \
#     chmod +x /res/chromedriver && \
#     rm chromedriver_linux64.zip 

WORKDIR /src

CMD ["python3", "recwell_bot.py"]