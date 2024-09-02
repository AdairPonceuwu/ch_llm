import streamlit as st
import time
import uuid

from assistant import get_answer
from db import (
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats,
)


def print_log(message):
    print(message, flush=True)


def main():
    print_log("Starting the CH Assistant application")
    st.title("Asistente del Centro Historico")

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(
            f"New conversation started with ID: {st.session_state.conversation_id}"
        )
    if "count" not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")

    if "last_conversation_id" not in st.session_state:
        st.session_state.last_conversation_id = None  # Para almacenar el ID de la conversación anterior

    # Topic selection
    topic = st.selectbox(
        "Selecciona un tema:",
        ["PMD", "PPDUS", "Consulta Ciudadana", "RUTA"],
    )
    print_log(f"User selected topic: {topic}")

    # Model selection
    model_choice = st.selectbox(
        "Selecciona un modelo:",
        ["ollama/llama3.1"],
    )
    print_log(f"User selected model: {model_choice}")

    # Search type selection
    search_type = st.radio("Selecciona el tipo de busqueda:", ["Text", "Vector"])
    print_log(f"User selected search type: {search_type}")

    # User input
    user_input = st.text_input("Ingresa tu pregunta:")

    if st.button("Preguntar"):
        print_log(f"User asked: '{user_input}'")
        with st.spinner("Disculpa, estoy pensando..."):
            print_log(
                f"Getting answer from assistant using {model_choice} model and {search_type} search"
            )
            start_time = time.time()
            answer_data = get_answer(user_input, topic, model_choice, search_type)
            end_time = time.time()
            print_log(f"Answer received in {end_time - start_time:.2f} seconds")
            st.success("Completado!")
            st.write(answer_data["answer"])

            # Display monitoring information
            st.write(f"Tiempo de respuesta: {answer_data['response_time']:.2f} seconds")
            st.write(f"Relevancia: {answer_data['relevance']}")
            st.write(f"Modelo usado: {answer_data['model_used']}")
            st.write(f"Total tokens: {answer_data['total_tokens']}")

            # Save conversation to database
            print_log("Saving conversation to database")
            save_conversation(
                st.session_state.conversation_id, user_input, answer_data, topic
            )
            print_log("Conversation saved successfully")

            # Store the last conversation ID for feedback purposes
            st.session_state.last_conversation_id = st.session_state.conversation_id

            # Generate a new conversation ID for the next question
            st.session_state.conversation_id = str(uuid.uuid4())
            print_log(
                f"New conversation ID generated for next question: {st.session_state.conversation_id}"
            )

    # Feedback buttons (linked to the last conversation ID)
    if st.session_state.last_conversation_id:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("+1"):
                st.session_state.count += 1
                print_log(
                    f"Positive feedback received. New count: {st.session_state.count}"
                )
                save_feedback(st.session_state.last_conversation_id, 1)
                print_log("Positive feedback saved to database")
        with col2:
            if st.button("-1"):
                st.session_state.count += 1
                print_log(
                    f"Negative feedback received. New count: {st.session_state.count}"
                )
                save_feedback(st.session_state.last_conversation_id, -1)
                print_log("Negative feedback saved to database")

    st.write(f"Feedbacks al momento: {st.session_state.count}")
    #st.write(f"Current Conversation ID: {st.session_state.conversation_id}")
    #st.write(f"Last Conversation ID: {st.session_state.last_conversation_id}")

    # Display recent conversations
    st.subheader("Conversaciones Recientes")
    relevance_filter = st.selectbox(
        "Filtrar por relevancia:", ["TODOS", "NO_RELEVANTE", "PARCIALMENTE_RELEVANTE", "RELEVANTE"]
    )
    recent_conversations = get_recent_conversations(
        limit=5, relevance=relevance_filter if relevance_filter != "TODOS" else None
    )
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write(f"Relevancia: {conv['relevance']}")
        st.write(f"Modelo: {conv['model_used']}")
        st.write("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Estadistica de los Feedbacks")
    st.write(f"Buenos: {feedback_stats['thumbs_up']}")
    st.write(f"Malos: {feedback_stats['thumbs_down']}")


print_log("Streamlit app loop completed")


if __name__ == "__main__":
    print_log("CH Assistant application started")
    main()
