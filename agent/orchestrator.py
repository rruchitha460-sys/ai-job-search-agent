from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from matching.resume_reader import extract_resume_text
import concurrent.futures

load_dotenv()

from agent.tools import (
    sourcing_tool,
    greenhouse_sourcing_tool,
    lever_sourcing_tool,
    matching_tool,
    filter_experience_tool,
)

# --- State ---
class AgentState(TypedDict):
    query: str
    location: str
    target_level: str
    resume_text: str
    jobs: list
    matches: list
    errors: list


# --- LLM for explanations (and, for now, tailoring too) ---
explanation_llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)

EXPLANATION_PROMPT = """You are helping a job seeker understand why a job matches their resume.

Resume summary: {resume_text}

Job:
Title: {title}
Company: {company}
Description: {description}

In 2-3 sentences, explain why this job is a good fit for this candidate, and mention
one thing they should highlight if they apply. Be specific, not generic."""

TAILORING_PROMPT = """You are a resume advisor helping a candidate tailor their resume for a specific job.

Candidate's resume:
{resume_text}

Target job:
Title: {title}
Company: {company}
Description: {description}

Give 3-4 specific, actionable suggestions for tailoring this resume to this job. For each suggestion,
say exactly what to change or add and why it matters for this specific role. Do not rewrite the whole
resume — just give targeted edits."""


def _extract_text(response) -> str:
    """Gemini's newer SDK returns content as a list of blocks
    (text + a 'signature' block for internal reasoning) — extract just the text parts."""
    if isinstance(response.content, list):
        return "".join(
            block.get("text", "") for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
    return response.content


# --- Nodes (part of the main graph) ---
def _fetch_source(tool_fn, name, query, location):
    try:
        if name == "lever":
            result = tool_fn.invoke({"query": query})
        else:
            result = tool_fn.invoke({"query": query, "location_filter": location})
        for j in result:
            j["source"] = name.capitalize()
        return name, result, None
    except Exception as e:
        return name, [], str(e)


def source_jobs(state: AgentState) -> AgentState:
    jobs, errors = [], []
    sources = [
        (sourcing_tool, "adzuna"),
        (greenhouse_sourcing_tool, "greenhouse"),
        (lever_sourcing_tool, "lever"),
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(_fetch_source, tool_fn, name, state["query"], state.get("location", ""))
            for tool_fn, name in sources
        ]
        for future in concurrent.futures.as_completed(futures):
            name, result, error = future.result()
            jobs.extend(result)
            if error:
                errors.append(f"{name}: {error}")

    return {**state, "jobs": jobs, "errors": errors}

def filter_jobs(state: AgentState) -> AgentState:
    filtered = filter_experience_tool.invoke({
        "jobs": state["jobs"],
        "target_level": state.get("target_level", "fresher"),
    })
    return {**state, "jobs": filtered}


def match_jobs(state: AgentState) -> AgentState:
    matches = matching_tool.invoke({
        "jobs": state["jobs"],
        "resume_text": state["resume_text"],
        "top_k": 5,
    })
    return {**state, "matches": matches}


def explain_matches(state: AgentState) -> AgentState:
    explained = []
    for job in state["matches"]:
        explanation_text = None
        for attempt in range(2):  # retry once on transient failures
            try:
                prompt = EXPLANATION_PROMPT.format(
                    resume_text=state["resume_text"][:500],
                    title=job.get("title"),
                    company=job.get("company"),
                    description=(job.get("description") or "")[:800],
                )
                response = explanation_llm.invoke(prompt)
                explanation_text = _extract_text(response)
                break  # success — stop retrying
            except Exception as e:
                if attempt == 1:  # last attempt failed too
                    print(f"Explanation error for {job.get('title')}: {e}")
        job["explanation"] = explanation_text
        explained.append(job)
    return {**state, "matches": explained}


def should_retry_sourcing(state: AgentState) -> str:
    if not state["jobs"] and len(state["errors"]) == 3:
        return "end"
    return "continue"


# --- Build graph ---
graph = StateGraph(AgentState)
graph.add_node("source", source_jobs)
graph.add_node("filter", filter_jobs)
graph.add_node("match", match_jobs)
graph.add_node("explain", explain_matches)

graph.set_entry_point("source")
graph.add_conditional_edges("source", should_retry_sourcing, {"continue": "filter", "end": END})
graph.add_edge("filter", "match")
graph.add_edge("match", "explain")
graph.add_edge("explain", END)

app_graph = graph.compile()


# --- Resume tailoring agent (NOT part of the graph — called on-demand from the UI) ---
def tailor_resume(resume_text: str, job: dict) -> str:
    """
    Generates specific resume tailoring suggestions for one job.
    Called on-demand (e.g. a button click per job), not as part of the main
    source->filter->match->explain graph, since it's low-volume and user-triggered.
    """
    try:
        prompt = TAILORING_PROMPT.format(
            resume_text=resume_text[:1500],  # more context than explanation agent — quality matters here
            title=job.get("title"),
            company=job.get("company"),
            description=(job.get("description") or "")[:1200],
        )
        response = explanation_llm.invoke(prompt)
        return _extract_text(response)
    except Exception as e:
        return f"Couldn't generate tailoring suggestions right now: {e}"


if __name__ == "__main__":
    result = app_graph.invoke({
        "query": "machine learning engineer",
        "location": "Bangalore",
        "target_level": "fresher",
        "resume_text": extract_resume_text(),
        "jobs": [],
        "matches": [],
        "errors": [],
    })
    print(f"\nFound {len(result['matches'])} matches after filtering {len(result['jobs'])} jobs\n")
    for m in result["matches"]:
        print(f"{m['rank']}. {m['title']} — {m['company']}")
        print(f"   {m.get('explanation')}\n")