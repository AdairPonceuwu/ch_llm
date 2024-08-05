---Install Ollama--- curl -fsSL https://ollama.com/install.sh | sh
---Start Ollama--- ollama start
---Run Sollama--- ollama run "model(Ex.phi3)"

---Ollama and docker--- 
docker run -it \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama

---Pulling a model inside Docker---
docker exec -it ollama bash 
--in ollama-- ollama pull phi3


---Running a Compose--- docker-compose up

---D: && cd \llm-ch\ch_llm---
