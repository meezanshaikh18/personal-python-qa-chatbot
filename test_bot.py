from chatbot import build_vectorizer, get_best_match, load_knowledge_base

# (question, text that must appear in the right answer,
#  or None if the bot should say "I don't know")
TESTS = [
    ("how do I install a library", "pip install"),
    ("what is a class", "blueprint"),
    ("how can I read a text file", "open("),
    ("remove duplicates from list", "unique items"),
    ("explain inheritance", "Inheritance lets"),
    ("how to handle errors", "try/except"),
    ("what is a tuple", "A tuple is"),
    ("difference between list and tuple", "A tuple is"),
    ("how to make text uppercase", ".upper()"),
    ("what does append do", "append"),
    ("how do I make a virtual environment", "virtual environment"),
    ("thanks", "welcome"),
    ("what is the capital of France", None),
    ("tell me a joke", None),
    ("bye", "Goodbye"),
]


def is_correct(expected, answer, score, threshold):
    if expected is None:
        return score < threshold  # bot should have declined
    return score >= threshold and expected in answer


if __name__ == "__main__":
    questions, answers = load_knowledge_base()
    vectorizer, matrix = build_vectorizer(questions)

    results = []
    for q, expected in TESTS:
        answer, score, matched = get_best_match(
            q, vectorizer, matrix, questions, answers
        )
        results.append((q, expected, answer, score, matched))

    print("Per-question results at THRESHOLD = 0.30")
    for q, expected, answer, score, matched in results:
        ok = is_correct(expected, answer, score, 0.30)
        print(f"{'PASS' if ok else 'FAIL'}  {score:.2f}  {q!r} -> {matched!r}")

    print("\nThreshold sweep:")
    for t in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        n = sum(is_correct(e, a, s, t) for _, e, a, s, _ in results)
        print(f"  {t:.1f}: {n}/{len(results)} correct")