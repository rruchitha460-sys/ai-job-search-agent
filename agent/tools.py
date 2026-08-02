from langchain_core.tools import tool
from ingestion.adzuna_client import search_jobs
from ingestion.greenhouse_client import search_greenhouse_jobs
from ingestion.lever_client import search_lever_jobs
from matching.embed import find_matches_in_jobs
from matching.experience_filter import filter_by_experience

@tool
def sourcing_tool(query: str, location: str = "Bangalore", results_per_page: int = 10) -> list:
    """Fetches job postings from Adzuna for a given query and location."""
    return search_jobs(query=query, location=location, results_per_page=results_per_page)


@tool
def greenhouse_sourcing_tool(query: str, location_filter: str = "") -> list:
    """Fetches job postings from Greenhouse-hosted company career pages."""
    return search_greenhouse_jobs(query=query, location_filter=location_filter)


@tool
def lever_sourcing_tool(query: str) -> list:
    """Fetches job postings from Lever-hosted company career pages."""
    return search_lever_jobs(query=query)


@tool
def matching_tool(jobs: list, resume_text: str, top_k: int = 5) -> list:
    """Ranks a list of job dicts against resume_text using FAISS + sentence embeddings."""
    return find_matches_in_jobs(jobs, resume_text, top_k=top_k)


@tool
def filter_experience_tool(jobs: list, target_level: str = "fresher") -> list:
    """Filters a list of job dicts by experience level."""
    return filter_by_experience(jobs, target_level)