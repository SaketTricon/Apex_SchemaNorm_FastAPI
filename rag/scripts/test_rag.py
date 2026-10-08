import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.index import load_index
from rag.vector_search import vector_search


INDEX_PATH = PROJECT_ROOT / "rag" / "data" / "knowledge_index.pkl"


def main() -> None:
	query = input("Enter your search query: ")
	index = load_index(INDEX_PATH)
	results = vector_search(query=query, index=index, top_k=5)

	print("\nRetrieved Knowledge")
	print("=" * 60)
	for result in results:
		print(f"\nSource: {result['source']}")
		print(f"Score: {result['score']:.4f}")
		print(f"Text:\n{result['text']}")


if __name__ == "__main__":
	main()
