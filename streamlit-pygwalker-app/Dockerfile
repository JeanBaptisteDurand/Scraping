FROM python:3.11-slim

# Dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ajout de la config Streamlit
RUN mkdir -p ~/.streamlit && \
    echo "\
[server]\n\
headless = true\n\
runOnSave = true\n\
maxMessageSize = 200\n\
requestTimeout = 300\n\
\n\
[browser]\n\
gatherUsageStats = false\n" > ~/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
