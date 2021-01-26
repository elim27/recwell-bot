FROM python:3.8-alpine3.12

COPY src/ /src/
COPY res/ /res/

RUN pip3 install -r /res/requirements.txt

WORKDIR /src

CMD ["python3", "recwell_bot.py"]