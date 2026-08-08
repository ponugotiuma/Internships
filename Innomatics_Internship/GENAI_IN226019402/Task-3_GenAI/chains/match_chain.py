def match_chain(resume_data, job_desc):
    return (match_prompt | llm).invoke({
        "resume_data": resume_data,
        "job_desc": job_desc
    })