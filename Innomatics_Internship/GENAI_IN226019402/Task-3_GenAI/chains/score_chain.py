def score_chain(match_data):
    return (score_prompt | llm).invoke({
        "match_data": match_data
    })