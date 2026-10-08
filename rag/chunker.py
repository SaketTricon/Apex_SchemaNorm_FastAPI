def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
	if chunk_size <= 0:
		raise ValueError("chunk_size must be greater than zero")

	words = text.split()
	return [
		" ".join(words[start : start + chunk_size])
		for start in range(0, len(words), chunk_size)
	]


def chunk_documents(
	documents: list[dict[str, str]], chunk_size: int = 500
) -> list[dict[str, str]]:
	chunks = []
	for document in documents:
		source = document["source"]
		for chunk_index, text in enumerate(
			chunk_text(document["content"], chunk_size)
		):
			chunks.append(
				{
					"id": f"{source}:{chunk_index}",
					"source": source,
					"text": text,
				}
			)
	return chunks
