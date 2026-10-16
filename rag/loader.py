from pathlib import Path


def load_documents(knowledge_dir: str | Path) -> list[dict[str, str]]:
	"""Load knowledge Markdown files, excluding README documentation."""
	root = Path(knowledge_dir)
	if not root.is_dir():
		raise FileNotFoundError(f"Knowledge directory not found: {root}")

	documents = []
	for file_path in sorted(root.rglob("*.md")):
		if file_path.name.lower() == "readme.md":
			continue
		documents.append(
			{
				"source": file_path.relative_to(root).as_posix(),
				"content": file_path.read_text(encoding="utf-8"),
			}
		)
	return documents
