import logging
from typing import Dict, Any, List, Optional
from app.services.github_service import GitHubService

logger = logging.getLogger(__name__)


class RepositoryDiscoveryAgent:
    """
    Responsibilities:
    - Search GitHub for relevant simulation implementations
    - Identify repositories matching the required domain and model
    - Collect repository metadata
    - Rank candidate repositories
    """
    def __init__(self, github_service: Optional[GitHubService] = None):
        self.github = github_service or GitHubService()

    async def discover_repositories(self, domain_or_model: str) -> List[Dict[str, Any]]:
        repos = await self.github.search_simulation_repositories(domain_or_model)
        
        # Rank by stars and permissive license
        ranked = sorted(
            repos,
            key=lambda r: (r.get("stars", 0) + (50 if r.get("license") in ("MIT", "Apache-2.0") else 0)),
            reverse=True
        )
        return ranked
