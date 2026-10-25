import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.index import load_index
from rag.vector_search import format_rag_context, vector_search


INDEX_PATH = PROJECT_ROOT / "rag" / "data" / "knowledge_index.pkl"


def main() -> None:
	query = input("Enter your query: ")
	
	index = load_index(INDEX_PATH)
	results = vector_search(query=query, index=index, top_k=5)
	context = format_rag_context(results)

	print("\nRAG Context")
	print("=" * 60)
	print(context)


if __name__ == "__main__":
	main()
