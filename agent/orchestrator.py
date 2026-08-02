from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from matching.resume_reader import extract_resume_text

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


# --- LLM for explanations ---
explanation_llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)

EXPLANATION_PROMPT = """You are helping a job seeker understand why a job matches their resume.

Resume summary: {resume_text}

Job:
Title: {title}
Company: {company}
Description: {description}

In 2-3 sentences, explain why this job is a good fit for this candidate, and mention
one thing they should highlight if they apply. Be specific, not generic."""


# --- Nodes ---
def source_jobs(state: AgentState) -> AgentState:
    jobs, errors = [], []
    for tool_fn, name in [
        (sourcing_tool, "adzuna"),
        (greenhouse_sourcing_tool, "greenhouse"),
        (lever_sourcing_tool, "lever"),
    ]:
        try:
            if name == "lever":
                result = tool_fn.invoke({"query": state["query"]})
            else:
                result = tool_fn.invoke({"query": state["query"], "location_filter": state.get("location", "")})
            jobs.extend(result)
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
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

                # Gemini's newer SDK returns content as a list of blocks
                # (text + a 'signature' block for internal reasoning) —
                # extract just the text parts.
                if isinstance(response.content, list):
                    explanation_text = "".join(
                        block.get("text", "") for block in response.content
                        if isinstance(block, dict) and block.get("type") == "text"
                    ).strip()
                else:
                    explanation_text = response.content
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