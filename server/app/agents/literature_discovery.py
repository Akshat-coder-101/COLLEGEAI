import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.literature_service import LiteratureService
from app.models.entities import ResearchPaper, Source

logger = logging.getLogger(__name__)


class LiteratureDiscoveryAgent:
    """
    Responsibilities:
    - Search for relevant research papers and publications
    - Discover papers related to the user's question
    - Collect paper titles, authors, abstracts, dates, and URLs
    - Deduplicate results and rank by relevance
    - Never fabricate citations or papers
    """
    def __init__(self, literature_service: Optional[LiteratureService] = None):
        self.lit_service = literature_service or LiteratureService()

    async def discover_literature(
        self,
        db: Session,
        project_id: str,
        queries: List[str],
        max_papers: int = 5
    ) -> Dict[str, Any]:
        discovered_papers = []
        limitations = []

        for q in queries[:3]:  # Top 3 search queries
            search_result = await self.lit_service.search_all(q, max_results=max_papers)
            discovered_papers.extend(search_result.get("papers", []))
            if search_result.get("limitation"):
                limitations.append(search_result["limitation"])

        # Deduplicate across query sets
        unique_papers = []
        seen = set()
        for p in discovered_papers:
            norm_title = "".join(filter(str.isalnum, p["title"].lower()))
            if norm_title and norm_title not in seen:
                seen.add(norm_title)
                unique_papers.append(p)

        saved_records = []
        for p in unique_papers[:max_papers]:
            paper_entity = ResearchPaper(
                project_id=project_id,
                title=p["title"],
                authors=p.get("authors", []),
                abstract=p.get("abstract"),
                publication_date=p.get("publication_date"),
                url=p.get("url"),
                doi=p.get("doi"),
                source_provider=p.get("source_provider", "external_api"),
                relevance_score=p.get("relevance_score", 0.8)
            )
            db.add(paper_entity)
            db.flush()

            # Create corresponding Source entity
            authors_str = ", ".join(p.get("authors", [])[:2]) or "Unknown"
            year = p.get("publication_date", "n.d.")
            citation = f"{authors_str} ({year}). {p['title'][:60]}..."

            source_entity = Source(
                project_id=project_id,
                paper_id=paper_entity.id,
                source_type="external_paper",
                citation_label=citation,
                metadata_info={"url": p.get("url"), "doi": p.get("doi"), "provider": p.get("source_provider")}
            )
            db.add(source_entity)
            db.flush()

            saved_records.append({
                "paper_id": paper_entity.id,
                "source_id": source_entity.id,
                "title": paper_entity.title,
                "authors": paper_entity.authors,
                "url": paper_entity.url
            })

        db.commit()

        return {
            "papers_discovered": len(saved_records),
            "records": saved_records,
            "limitations": list(set(limitations))
        }
