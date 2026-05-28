
PROMPT_VERSION = "paper_summary_v1"

def build_paper_summary_prompt(title: str, abstract:str)->str:
    return f"""
summarize this research paper for a researcher. 

Title: {title}

Abstract:
{abstract}

Write 3-5 concise bullet points for TL;DR. Focus on:
- the main problem this paper is trying to solve
- the method
- experiment setup and the key result
- why it matters
""".strip()
