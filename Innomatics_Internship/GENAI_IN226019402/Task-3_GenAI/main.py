# ── IMPORTS ───────────────────────────────────────────────
from fastapi import FastAPI
from pydantic import BaseModel

# Import your chains
from chains.extract_chain import extract_chain
from chains.match_chain import match_chain
from chains.score_chain import score_chain
from chains.explain_chain import explain_chain

# ── APP INIT ──────────────────────────────────────────────
app = FastAPI(title="AI Resume Screening System")

# ── REQUEST MODEL ─────────────────────────────────────────
class ResumeRequest(BaseModel):
    resume: str
    job_description: str

# ── MAIN PIPELINE ─────────────────────────────────────────
def run_pipeline(resume: str, job_desc: str):

    # Step 1: Extract
    extracted = extract_chain(resume)

    # Step 2: Match
    matched = match_chain(extracted, job_desc)

    # Step 3: Score
    score = score_chain(matched, extracted.get("experience", 0))

    # Step 4: Explain
    explanation = explain_chain(matched, score, extracted.get("experience", 0))

    return {
        "extracted": extracted,
        "matched": matched,
        "score": score,
        "explanation": explanation
    }

# ── API ENDPOINTS ─────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Resume Screening API Running"}

@app.post("/screen")
def screen_resume(data: ResumeRequest):
    return run_pipeline(data.resume, data.job_description)

# ── TEST ENDPOINTS (FOR SCREENSHOTS) ───────────────────────

@app.get("/test/strong")
def test_strong():
    resume = """
    Data Scientist with 3+ years experience.
    Skills: Python, Machine Learning, SQL, Deep Learning
    """
    job_desc = """
    Data Scientist role: Python, Machine Learning, SQL, Data Analysis
    """
    return run_pipeline(resume, job_desc)


@app.get("/test/average")
def test_average():
    resume = """
    Junior Developer with 1 year experience.
    Skills: Python, basic Machine Learning
    """
    job_desc = """
    Data Scientist role: Python, Machine Learning, SQL, Data Analysis
    """
    return run_pipeline(resume, job_desc)


@app.get("/test/weak")
def test_weak():
    resume = """
    Fresher with no relevant experience.
    Skills: Excel, Communication
    """
    job_desc = """
    Data Scientist role: Python, Machine Learning, SQL, Data Analysis
    """
    return run_pipeline(resume, job_desc)

