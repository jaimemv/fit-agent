from app.models.domain import KnowledgeSnippet
from app.repositories.base import Repository


class KnowledgeAgent:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def answer(self, query: str) -> tuple[str, list[str]]:
        snippets = self.repository.search_knowledge(query=query, limit=3)
        notes = [self._format_snippet(snippet) for snippet in snippets]
        answer = (
            "Here is evidence-informed guidance based on your knowledge base. "
            "For medical concerns, defer to licensed professionals."
        )
        return answer, notes

    def _format_snippet(self, snippet: KnowledgeSnippet) -> str:
        return f"{snippet.source} ({snippet.topic}): {snippet.note}"
