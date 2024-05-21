FROM python:3.12
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1


RUN apt update && apt upgrade && python -m pip install --upgrade pip

WORKDIR app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY common common
COPY camera camera

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "camera"]
