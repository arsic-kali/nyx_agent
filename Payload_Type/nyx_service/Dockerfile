FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y binutils && rm -rf /var/lib/apt/lists/*
RUN pip install mythic_container requests pyinstaller

CMD ["python3", "main.py"]