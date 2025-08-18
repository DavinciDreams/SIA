from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any
from orchestrator import Orchestrator
from config import SIA_API_KEY

def api_key_auth(request: Request):
    api_key = request.headers.get("x-api-key")
    if not api_key or api_key != SIA_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True

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
    prompt: str
    reviewers: Optional[list] = []
    auto: Optional[bool] = False

class PRStatusRequest(BaseModel):
    repo_url: str
    pr_id: int

class PRResponse(BaseModel):
    result: str
    pr_id: Optional[int] = None

class PRStatusResponse(BaseModel):
    status: str

class ManualMemoryInjectRequest(BaseModel):
    text: str
    meta: Optional[dict] = None
    memory_type: str = "semantic"

class ManualMemoryInjectResponse(BaseModel):
    index: int

class ManualMemoryRetrieveResponse(BaseModel):
    memory: Optional[Any]

@app.post("/memory/store", response_model=MemoryStoreResponse)
async def memory_store(req: MemoryStoreRequest, auth: bool = Depends(api_key_auth)):
    """
    Store text in memory with optional metadata.
    """
    result = orchestrator.memory_store(req.text, meta=req.meta)
    return MemoryStoreResponse(result=result)

@app.post("/memory/retrieve", response_model=MemoryRetrieveResponse)
async def memory_retrieve(req: MemoryRetrieveRequest, auth: bool = Depends(api_key_auth)):
    """
    Retrieve memories matching a query.
    """
    results = orchestrator.memory_retrieve(req.query, topk=req.topk)
    return MemoryRetrieveResponse(results=results)

@app.post("/memory/manual_inject", response_model=ManualMemoryInjectResponse)
async def manual_memory_inject(req: ManualMemoryInjectRequest, auth: bool = Depends(api_key_auth)):
    """
    Manually inject a memory (bypassing embedding/index).
    Supports all memory types: episodic, semantic, procedural.
    """
    idx = orchestrator.memory_module.inject_memory(
        text=req.text,
        meta=req.meta,
        memory_type=req.memory_type
    )
    return ManualMemoryInjectResponse(index=idx)

@app.get("/memory/manual_retrieve", response_model=ManualMemoryRetrieveResponse)
async def manual_memory_retrieve(idx: int, auth: bool = Depends(api_key_auth)):
    """
    Retrieve a memory by its index.
    Returns the memory dict or null if not found.
    """
    mem = orchestrator.memory_module.get_memory(idx)
    return ManualMemoryRetrieveResponse(memory=mem)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, auth: bool = Depends(api_key_auth)):
    """
    Run code analysis and reporting.
    """
    report = orchestrator.run_self_analysis_cycle(
        code_paths=req.paths,
        report_format=req.format
    )
    return AnalyzeResponse(report=report)

@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, auth: bool = Depends(api_key_auth)):
    """
    Generate code for a specified task and write to file.
    """
    result = orchestrator.generate_code(
        prompt=req.prompt,
        file_path=req.file_path
    )
    return GenerateResponse(result=result)

@app.post("/pr", response_model=PRResponse)
async def pr(req: PRRequest, auth: bool = Depends(api_key_auth)):
    """
    Automate code generation and PR submission workflow with enhancements.
    """
    if req.auto:
        analysis_summary = orchestrator.run_self_analysis_cycle(code_paths=[req.file_path], report_format="markdown")
        pr_title, pr_description = orchestrator.integration_module.generate_pr_metadata(analysis_summary, req.prompt)
    else:
        pr_title = getattr(req, "pr_title", "Automated PR")
        pr_description = getattr(req, "pr_description", req.prompt)
    result, pr_id = orchestrator.automate_code_and_pr_workflow(
        repo_url=req.repo_url,
        file_path=req.file_path,
        branch_name=req.branch_name,
        pr_title=pr_title,
        pr_description=pr_description,
        prompt=req.prompt,
        return_pr_id=True
    )
    if req.reviewers:
        orchestrator.integration_module.assign_reviewers(req.repo_url, pr_id, req.reviewers)
    return PRResponse(result=result, pr_id=pr_id)

class ApprovePRRequest(BaseModel):
    pr_id: int

class ApprovePRResponse(BaseModel):
    result: str

@app.post("/pr/approve", response_model=ApprovePRResponse)
async def approve_pr(req: ApprovePRRequest, auth: bool = Depends(api_key_auth)):
    """
    Approve and merge a PR by PR ID.
    """
    result = orchestrator.approve_and_merge_pr(req.pr_id)
    return ApprovePRResponse(result=result)

class RollbackPRRequest(BaseModel):
    pr_id: int

class RollbackPRResponse(BaseModel):
    result: str

@app.post("/pr/rollback", response_model=RollbackPRResponse)
async def rollback_pr(req: RollbackPRRequest, auth: bool = Depends(api_key_auth)):
    """
    Rollback a PR's self-improvement by PR ID.
    """
    result = orchestrator.rollback_self_improvement(req.pr_id)
    return RollbackPRResponse(result=result)

@app.post("/pr/status", response_model=PRStatusResponse)
async def pr_status(req: PRStatusRequest, auth: bool = Depends(api_key_auth)):
    """
    Get the status of a pull request.
    """
    status = orchestrator.integration_module.monitor_pr_status(req.repo_url, req.pr_id)
    return PRStatusResponse(status=status)