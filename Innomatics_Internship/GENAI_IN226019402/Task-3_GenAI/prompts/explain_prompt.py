explain_prompt = PromptTemplate(
    input_variables=["match_data", "score"],
    template="""
Explain why this score was given.

Include:
- Strengths
- Weaknesses

Match Data:
{match_data}

Score:
{score}
"""
)