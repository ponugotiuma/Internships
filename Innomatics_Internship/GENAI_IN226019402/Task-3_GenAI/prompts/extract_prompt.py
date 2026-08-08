from langchain.prompts import PromptTemplate

extract_prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
Extract the following from the resume:
- Skills
- Experience
- Tools

Return in JSON format.

Resume:
{resume}

IMPORTANT:
Do NOT assume anything not present.
"""
)
