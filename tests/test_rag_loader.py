import tempfile
import unittest
from pathlib import Path

from rag.loader import load_documents


class RagLoaderTests(unittest.TestCase):
	def test_excludes_readme_files_from_knowledge_documents(self):
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder)
			(root / "README.md").write_text("Folder documentation", encoding="utf-8")
			knowledge = root / "normalization"
			knowledge.mkdir()
			(knowledge / "README.md").write_text("Section documentation", encoding="utf-8")
			(knowledge / "third_normal_form.md").write_text(
				"Normalization guidance", encoding="utf-8"
			)

			documents = load_documents(root)

		self.assertEqual(
			documents,
			[
				{
					"source": "normalization/third_normal_form.md",
					"content": "Normalization guidance",
				}
			],
		)


if __name__ == "__main__":
	unittest.main()
