# syntax=docker/dockerfile:1
FROM python:3.8
COPY . /OTRPO_Lab1
WORKDIR /OTRPO_Lab1
EXPOSE 80
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]