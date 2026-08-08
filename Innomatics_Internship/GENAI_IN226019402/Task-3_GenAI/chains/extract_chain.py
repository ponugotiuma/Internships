from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")

def extract_chain(resume):
    return (extract_prompt | llm).invoke({"resume": resume})
