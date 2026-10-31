import json
import re
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK resources when possible. If they are unavailable (for example,
# on an offline machine), use a lightweight fallback so the chatbot can still run.
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

try:
    ENGLISH_STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as SKLEARN_STOP_WORDS
    ENGLISH_STOP_WORDS = set(SKLEARN_STOP_WORDS)

# Keep "not" and "no": they change the meaning of a question
ENGLISH_STOP_WORDS -= {"not", "no"}
# Every question here is about Python, so "python" normally tells us nothing
STOP_WORDS = ENGLISH_STOP_WORDS | {"python"}
lemmatizer = WordNetLemmatizer()


def safe_lemmatize(token):
    """Use WordNet lemmatization when its corpus is available; otherwise keep the token."""
    try:
        return lemmatizer.lemmatize(token)
    except LookupError:
        return token

THRESHOLD = 0.3
FALLBACK = (
    "Sorry, I don't know that one yet. "
    "Try asking about lists, tuples, dictionaries, loops, functions or strings."
)


def preprocess(text):
    """Lowercase, strip punctuation, drop stopwords, lemmatize."""
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    kept = [safe_lemmatize(t) for t in tokens if t not in STOP_WORDS]
    if not kept:
        # e.g. "what is python": nothing is left, so keep "python" this time
        kept = [safe_lemmatize(t) for t in tokens if t not in ENGLISH_STOP_WORDS]
    return " ".join(kept)


def load_knowledge_base(folder="data"):
    """Read every .json file in the folder into parallel question/answer lists."""
    questions, answers = [], []
    for path in sorted(Path(folder).glob("*.json")):
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            for q in entry["questions"]:
                questions.append(q)
                answers.append(entry["answer"])
    return questions, answers


def build_vectorizer(questions):
    """Learn the vocabulary and turn every stored question into a TF-IDF vector."""
    processed = [preprocess(q) for q in questions]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(processed)
    return vectorizer, matrix


def get_best_match(user_question, vectorizer, matrix, questions, answers):
    """Return (answer, score, matched_question) for the closest stored question."""
    query_vector = vectorizer.transform([preprocess(user_question)])
    scores = cosine_similarity(query_vector, matrix).flatten()
    best = scores.argmax()
    return answers[best], float(scores[best]), questions[best]


def answer_question(user_question, vectorizer, matrix, questions, answers):
    """Return (reply, score, matched_question), or the fallback if confidence is low."""
    answer, score, matched = get_best_match(
        user_question, vectorizer, matrix, questions, answers
    )
    if score < THRESHOLD:
        return FALLBACK, score, matched
    return answer, score, matched


if __name__ == "__main__":
    questions, answers = load_knowledge_base()
    vectorizer, matrix = build_vectorizer(questions)
    print(f"Loaded {len(questions)} question phrasings")

    tests = ["hello", "what is python", "how do I write a for loop", "weather today"]
    for test in tests:
        reply, score, matched = answer_question(
            test, vectorizer, matrix, questions, answers
        )
        print(f"{test!r} -> {matched!r} (score {score:.2f})")