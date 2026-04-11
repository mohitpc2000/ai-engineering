from get_embedding import get_embedding
from similarity import find_most_similar
SNIPPETS = [
    "How to sign out from your account",
    "Reset your password via email link",
    "Set up two-factor authentication",
    "Permanently delete your account",
    "Change your display name and avatar",
    "Update your billing and payment info",
    "View your order and purchase history",
    "Reach out to customer support",
    "Switch to dark mode in settings",
    "Download and export your data",
]
def build_knowledge_base(snippets):
    print("Indexing snippets...")
    knowledge_base = []
    for i, snippet in enumerate(snippets):
        print(f" Processing snippet {i+1}/{len(snippets)} {snippet}")
        embedding = get_embedding(snippet)
        knowledge_base.append({
            'text': snippet,
            'embedding': embedding
        })
    print(f"Done, {len(knowledge_base)} snippets indexed.\n")
    return knowledge_base
def search(query, knowledge_base):
    query_embedding = get_embedding(query)
    return find_most_similar(query_embedding, knowledge_base)
def main():
    print("=== Semantic Search CLI ===\n")
    knowledge_base = build_knowledge_base(SNIPPETS);
    while True:
        query = input("Your question (or 'quit'): ").strip()
        if query.lower() == 'quit':
            print("Goodbye!")
            break
        if not query:
            print("Please enter a valid question.\n")
            continue
        results = search(query, knowledge_base)
        print(f"\n Results for '{query}':")
        print("-" * 40)
        for rank,(text,score) in enumerate(results, start=1):
            print(f"{rank}.{text}\n")
            print(f"   Similarity: {score:.4f}\n")
        print()
if __name__ == "__main__":
    main()