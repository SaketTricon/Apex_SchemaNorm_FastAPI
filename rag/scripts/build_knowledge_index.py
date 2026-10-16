import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.index import build_index


if __name__ == "__main__":
	index = build_index(
		knowledge_dir=PROJECT_ROOT / "rag" / "knowledge",
		output_file=PROJECT_ROOT / "rag" / "data" / "knowledge_index.pkl",
	)
	print(f"Created index with {len(index['chunks'])} chunks")
