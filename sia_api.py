from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any
from orchestrator import Orchestrator

app = FastAPI(
    title="SIA API",
    description="API for memory operations, code analysis, code generation, and PR submission.",
    version="1.0.0"
)

orchestrator = Orchestrator()

class MemoryStoreRequest(BaseModel):
    text: str
    meta: Optional[str] = None

class MemoryStoreResponse(BaseModel):
    result: Any

class MemoryRetrieveRequest(BaseModel):
    query: str
    topk: int = 3

class MemoryRetrieveResponse(BaseModel):
    results: List[Any]

class AnalyzeRequest(BaseModel):
    paths: Optional[List[str]] = None
    format: str = "markdown"

class AnalyzeResponse(BaseModel):
    report: str

class GenerateRequest(BaseModel):
    prompt: str
    file_path: str

class GenerateResponse(BaseModel):
    result: str

class PRRequest(BaseModel):
    repo_url: str
    file_path: str
    branch_name: str
    pr_title: str
    pr_description: str
    prompt: str

class PRResponse(BaseModel):
    result: str

@app.post("/memory/store", response_model=MemoryStoreResponse)
async def memory_store(req: MemoryStoreRequest):
    """
    Store text in memory with optional metadata.
    """
    result = orchestrator.memory_store(req.text, meta=req.meta)
    return MemoryStoreResponse(result=result)

@app.post("/memory/retrieve", response_model=MemoryRetrieveResponse)
async def memory_retrieve(req: MemoryRetrieveRequest):
    """
    Retrieve memories matching a query.
    """
    results = orchestrator.memory_retrieve(req.query, topk=req.topk)
    return MemoryRetrieveResponse(results=results)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Run code analysis and reporting.
    """
    report = orchestrator.run_self_analysis_cycle(
        code_paths=req.paths,
        report_format=req.format
    )
    return AnalyzeResponse(report=report)

@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    """
    Generate code for a specified task and write to file.
    """
    result = orchestrator.generate_code(
        prompt=req.prompt,
        file_path=req.file_path
    )
    return GenerateResponse(result=result)

@app.post("/pr", response_model=PRResponse)
async def pr(req: PRRequest):
    """
    Automate code generation and PR submission workflow.
    """
    result = orchestrator.automate_code_and_pr_workflow(
        repo_url=req.repo_url,
        file_path=req.file_path,
        branch_name=req.branch_name,
        pr_title=req.pr_title,
        pr_description=req.pr_description,
        prompt=req.prompt
    )
    return PRResponse(result=result)