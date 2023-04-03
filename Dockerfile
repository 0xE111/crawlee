FROM python:3.10
WORKDIR /home

COPY requirements.txt ./
RUN pip3 install --no-cache-dir --upgrade pip  -r requirements.txt

COPY src ./
CMD ["python", "bot.py"]
