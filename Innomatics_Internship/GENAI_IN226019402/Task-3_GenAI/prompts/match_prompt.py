match_prompt = PromptTemplate(
    input_variables=["resume_data", "job_desc"],
    template="""
Compare the resume with job description.

Return:
- Matching skills
- Missing skills

Resume Data:
{resume_data}

Job Description:
{job_desc}
"""
)