import json
from pathlib import Path
from typing import List, Dict, Optional
from src.agentic_os.schemas.corpus import EvidenceSnippet, OutcomeCategory, SourceType


class CorpusLoader:
    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            data_path = Path(__file__).parent / "seed_data.json"
        self.data_path = data_path
        self._snippets: List[EvidenceSnippet] = []
        self._index_by_id: Dict[str, EvidenceSnippet] = {}
        self._index_by_cat: Dict[OutcomeCategory, List[EvidenceSnippet]] = {}
        self.reload()

    def reload(self) -> None:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Corpus file not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        self._snippets = [EvidenceSnippet(**item) for item in raw_data]
        self._index_by_id = {s.snippet_id: s for s in self._snippets}
        self._index_by_cat = {}
        for s in self._snippets:
            self._index_by_cat.setdefault(s.category, []).append(s)

    def get_all(self) -> List[EvidenceSnippet]:
        return list(self._snippets)

    def get_by_id(self, snippet_id: str) -> Optional[EvidenceSnippet]:
        return self._index_by_id.get(snippet_id)

    def get_by_category(self, category: OutcomeCategory) -> List[EvidenceSnippet]:
        return self._index_by_cat.get(category, [])

    def count(self) -> int:
        return len(self._snippets)

    def available_categories(self) -> List[OutcomeCategory]:
        return list(self._index_by_cat.keys())
