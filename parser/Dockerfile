FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parser.py .

COPY trigger.py .

CMD sh -c "python -u trigger.py & python -u parser.py"
