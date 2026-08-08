def explain_chain(match_data, score):
    return (explain_prompt | llm).invoke({
        "match_data": match_data,
        "score": score
    })