import os
import time
import json

from openai import OpenAI

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")


es_client = Elasticsearch(ELASTIC_URL)
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


def elastic_search_text(query, topic, index_name = "ch-questions"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {"term": {"topic": topic}},
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    return [hit["_source"] for hit in response["hits"]["hits"]]


def elastic_search_knn_combined(vector, topic, index_name="ch-questions"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": [
                    {
                        "script_score": {
                            "query": {
                                "term": {
                                    "topic": topic
                                }
                            },
                            "script": {
                                "source": """
                                    cosineSimilarity(params.query_vector, 'question_vector') + 
                                    cosineSimilarity(params.query_vector, 'text_vector') + 
                                    cosineSimilarity(params.query_vector, 'question_text_vector') + 
                                    1
                                """,
                                "params": {
                                    "query_vector": vector
                                }
                            }
                        }
                    }
                ],
                "filter": {
                    "term": {
                        "topic": topic
                    }
                }
            }
        },
        "_source": ["text", "section", "question", "topic", "id"]
    }

    es_results = es_client.search(index=index_name, body=search_query)

    return [hit["_source"] for hit in es_results["hits"]["hits"]]

def build_prompt(query, search_results):
    prompt_template = """
    Tu eres un experto en el municipio de Puebla y el Centro Histórico de Puebla. Responde la PREGUNTA basandote en el CONTEXTO proveniente de la base de datos FAQ.
    Se conciso, claro y da la mejor respuesta. Usando unicamente los hechos provenientes del CONTEXTO cuando respondas la PREGUNTA.

    PREGUNTA: {question}

    CONTEXTO 
    {context}
    """.strip()

    context = "\n\n".join(
        [
            f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}"
            for doc in search_results
        ]
    )
    return prompt_template.format(question=query, context=context).strip()


def llm(prompt, model_choice):
    start_time = time.time()
    if model_choice.startswith('ollama/'):
        response = ollama_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    return answer, tokens, response_time


def evaluate_relevance(question, answer):
    prompt_template = """
    Eres un evaluador experto para un sistema de Generación Aumentada por Recuperación (RAG).
    Tu tarea es analizar la relevancia de la respuesta generada en relación con la pregunta dada.
    Con base en la relevancia de la respuesta generada, la clasificarás
    como "NO_RELEVANTE", "PARCIALMENTE_RELEVANTE" o "RELEVANTE".

    Aquí están los datos para la evaluación:

    Pregunta: {question}
    Respuesta Generada: {answer}

    Por favor, analiza el contenido y contexto de la respuesta generada en relación con la pregunta
    y proporciona tu evaluación en JSON sin usar bloques de código:

    {{
    "Relevancia": "NO_RELEVANTE" | "PARCIALMENTE_RELEVANTE" | "RELEVANTE",
    "Explicación": "[Proporciona una breve explicación para tu evaluación]"
    }}
    """.strip()

    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, 'ollama/llama3.1')
    
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevancia'], json_eval['Explicación'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens


def get_answer(query, topic, model_choice, search_type):
    if search_type == 'Vector':
        vector = model.encode(query)
        search_results = elastic_search_knn_combined(vector, topic)
    else:
        search_results = elastic_search_text(query, topic)

    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model_choice)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

 
    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
    }