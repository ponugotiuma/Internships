score_prompt = PromptTemplate(
    input_variables=["match_data"],
    template="""
Based on the match data, assign a score (0–100).

Rules:
- More matches → higher score
- Missing critical skills → reduce score

Return only:
Score: <number>
"""
)