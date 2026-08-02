import re

# Patterns that signal a SENIOR-level requirement
SENIOR_PATTERNS = [
    r'\b(\d+)\s*\+?\s*(?:to\s*\d+\s*)?years?\b',  # "5+ years", "5 to 8 years"
    r'\bsenior\b',
    r'\blead\b',
    r'\bprincipal\b',
    r'\bmanager\b',
    r'\bhead\s+of\b',
    r'\bdirector\b',
    r'\bvp\b',
    r'\bvice\s+president\b',
    r'\b\d+\+\s*yrs?\b',
]

# Patterns that signal ENTRY-level / fresher friendly
ENTRY_PATTERNS = [
    r'\bfresher\b',
    r'\bentry[\s-]?level\b',
    r'\bgraduate\b',
    r'\bintern(?:ship)?\b',
    r'\b0\s*[-–to]+\s*[12]\s*years?\b',
    r'\bjunior\b',
    r'\btrainee\b',
    r'\bno\s+experience\s+required\b',
]


def extract_min_years(description):
    """Try to find the minimum years of experience mentioned in a job description."""
    if not description:
        return None

    text = description.lower()

    # Look for patterns like "5+ years", "3-5 years", "minimum 5 years"
    matches = re.findall(r'(\d+)\s*\+?\s*(?:-|to)?\s*\d*\s*years?', text)
    if matches:
        years = [int(m) for m in matches if m.isdigit()]
        if years:
            return min(years)

    return None


def classify_experience_level(description):
    """
    Roughly classify a job description as 'entry', 'senior', or 'unclear'
    based on keyword patterns and mentioned years of experience.
    """
    if not description:
        return "unclear"

    text = description.lower()

    min_years = extract_min_years(text)

    entry_signals = any(re.search(p, text) for p in ENTRY_PATTERNS)
    senior_signals = any(re.search(p, text) for p in SENIOR_PATTERNS)

    if min_years is not None:
        if min_years <= 2:
            return "entry"
        elif min_years >= 4:
            return "senior"

    if entry_signals and not senior_signals:
        return "entry"
    if senior_signals and not entry_signals:
        return "senior"

    return "unclear"


def filter_by_experience(jobs, target_level):
    """
    Filter a list of job dicts to only those matching the target experience level.
    target_level: 'fresher' (0-2 yrs), 'mid' (2-5 yrs), 'senior' (5+ yrs), or 'any'

    Jobs classified as 'unclear' are kept (benefit of the doubt) rather than dropped,
    since many postings don't clearly state experience requirements.
    """
    if target_level == "any":
        return jobs

    filtered = []
    for job in jobs:
        level = classify_experience_level(job.get("description"))

        if target_level == "fresher":
            # Keep entry-level and unclear jobs; drop clearly senior ones
            if level != "senior":
                filtered.append(job)
        elif target_level == "senior":
            # Keep senior and unclear jobs; drop clearly entry-level ones
            if level != "entry":
                filtered.append(job)
        else:  # mid-level: keep everything except extreme senior titles
            filtered.append(job)

    return filtered


def query_suffix_for_level(target_level):
    """Return a keyword suffix to append to the Adzuna search query for better source results."""
    if target_level == "fresher":
        return " fresher entry level"
    elif target_level == "senior":
        return " senior"
    return ""