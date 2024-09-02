import time
import random
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from db import save_conversation, save_feedback, get_db_connection

# Set the timezone to CET (Europe/Berlin)
tz = ZoneInfo("America/Mexico_City")

# List of sample questions and answers
SAMPLE_QUESTIONS = [
    "¿Cuál es el porcentaje de viviendas con apenas un dormitorio en el Centro Histórico?",
    "¿Dónde se encuentran las mayores condiciones de pobreza y marginación en el Centro Histórico de Puebla?",
    "¿Qué medidas se considerarán para la implementación de la intermodalidad entre el sistema RUTA y el transporte público interbarrial?",
    "¿Cuáles son las principales características de la organización de RUTA?",
    "¿Qué elementos se incluirán en la construcción de Paseos Seguros para fomentar la movilidad peatonal y no motorizada?",
]

SAMPLE_ANSWERS = [
    "El 34.9'%' de las viviendas en el Centro Histórico de Puebla cuentan con apenas un dormitorio, lo que indica una condición de hacinamiento.",
    "Las mayores condiciones de pobreza y marginación en el Centro Histórico de Puebla se encuentran en los barrios de San Sebastián, San Matías, San Antonio, Santa Anita, El Refugio, San Miguel, Xonaca, Xanenetla, El Alto, La Luz, Analco, y algunas áreas de la colonia Centro.",
    "Para la implementación de la intermodalidad entre el sistema RUTA y el transporte público interbarrial, se consideran medidas como la creación de cruceros seguros, la instalación de semáforos, y la señalización vertical.",
    "La organización del sistema RUTA se caracteriza por su estructura administrativa y operativa, que incluye 3 líneas troncales y 32 rutas alimentadoras.",
    "En la construcción de Paseos Seguros se incluirán elementos como ciclocarriles, carriles confinados para ciclistas, ampliación de la banqueta, y adecuación del mobiliario urbano, garantizando un libre tránsito del peatón y la accesibilidad.",
]


TOPIC = ["PMD", "PPDUS", "Consulta Ciudadana", "RUTA"]
MODELS = ["ollama/llama3.1"]
RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]


def generate_synthetic_data(start_time, end_time):
    current_time = start_time
    conversation_count = 0
    print(f"Starting historical data generation from {start_time} to {end_time}")
    while current_time < end_time:
        conversation_id = str(uuid.uuid4())
        question = random.choice(SAMPLE_QUESTIONS)
        answer = random.choice(SAMPLE_ANSWERS)
        topic = random.choice(TOPIC)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

 
        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 5.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} to the question.",
            "model_used": model,
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(50, 300),
            "total_tokens": random.randint(100, 500),
            "eval_prompt_tokens": random.randint(50, 150),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 250),
        }

        save_conversation(conversation_id, question, answer_data, topic, current_time)
        print(
            f"Saved conversation: ID={conversation_id}, Time={current_time}, Topic={topic}, Model={model}"
        )

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time)
            print(
                f"Saved feedback for conversation {conversation_id}: {'Positive' if feedback > 0 else 'Negative'}"
            )

        current_time += timedelta(minutes=random.randint(1, 15))
        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} conversations so far...")

    print(
        f"Historical data generation complete. Total conversations: {conversation_count}"
    )


def generate_live_data():
    conversation_count = 0
    print("Starting live data generation...")
    while True:
        current_time = datetime.now(tz)
        # current_time = None
        conversation_id = str(uuid.uuid4())
        question = random.choice(SAMPLE_QUESTIONS)
        answer = random.choice(SAMPLE_ANSWERS)
        topic = random.choice(TOPIC)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 5.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} to the question.",
            "model_used": model,
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(50, 300),
            "total_tokens": random.randint(100, 500),
            "eval_prompt_tokens": random.randint(50, 150),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 250),
        }

        save_conversation(conversation_id, question, answer_data, topic, current_time)
        print(
            f"Saved live conversation: ID={conversation_id}, Time={current_time}, Topic={topic}, Model={model}"
        )

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time)
            print(
                f"Saved feedback for live conversation {conversation_id}: {'Positive' if feedback > 0 else 'Negative'}"
            )

        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} live conversations so far...")

        time.sleep(1)


if __name__ == "__main__":
    print(f"Script started at {datetime.now(tz)}")
    end_time = datetime.now(tz)
    start_time = end_time - timedelta(hours=6)
    print(f"Generating historical data from {start_time} to {end_time}")
    generate_synthetic_data(start_time, end_time)
    print("Historical data generation complete.")

    print("Starting live data generation... Press Ctrl+C to stop.")
    try:
        generate_live_data()
    except KeyboardInterrupt:
        print(f"Live data generation stopped at {datetime.now(tz)}.")
    finally:
        print(f"Script ended at {datetime.now(tz)}")