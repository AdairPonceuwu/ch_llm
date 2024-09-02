Run docker-compose
docker-compose up

To download the llama3.1 model to the container
docker-compose up 
docker-compose exec ollama ollama pull llama3.1

Run one time
prep.py 

postgres
pgcli -h localhost -U your_username -d ch_assistant -W