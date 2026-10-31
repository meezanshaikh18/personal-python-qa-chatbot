from chatbot import answer_question, build_vectorizer, load_knowledge_base


def main():
    questions, answers = load_knowledge_base()
    vectorizer, matrix = build_vectorizer(questions)

    print("Python Q&A Bot - ask me a Python question. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Bot: Goodbye!")
            break
        if not user_input:
            continue

        reply, score, matched = answer_question(
            user_input, vectorizer, matrix, questions, answers
        )
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()