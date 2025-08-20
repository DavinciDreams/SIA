"""
Validation utilities for SIA Dashboard UI.
"""

import json
import re

def validate_memory_type(memory_type):
    if memory_type not in {"episodic", "semantic", "procedural"}:
        raise ValueError("Invalid memory type. Must be episodic, semantic, or procedural.")
    return memory_type

def validate_text(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string.")
    return text

def validate_meta(meta_str):
    if not meta_str.strip():
        return {}
    try:
        meta = json.loads(meta_str)
        if not isinstance(meta, dict):
            raise ValueError("Meta must be a JSON object.")
        return meta
    except Exception:
        raise ValueError("Meta must be valid JSON.")

def validate_index(idx):
    try:
        idx_int = int(idx)
        if idx_int < 0:
            raise ValueError("Index must be non-negative.")
        return idx_int
    except Exception:
        raise ValueError("Index must be a non-negative integer.")

def validate_repo_url(url):
    pattern = r"^https://github\.com/[\w\-]+/[\w\-]+$"
    if not re.match(pattern, url):
        raise ValueError("Repo URL must be a valid GitHub repository URL.")
    return url

def validate_branch_name(branch):
    if not isinstance(branch, str) or not branch.strip():
        raise ValueError("Branch name must be a non-empty string.")
    return branch

def validate_prompt_text(prompt_text):
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        raise ValueError("Prompt text must be a non-empty string.")
    return prompt_text

def validate_reviewers(reviewers):
    if not isinstance(reviewers, list):
        raise ValueError("Reviewers must be a list.")
    for r in reviewers:
        if r and not isinstance(r, str):
            raise ValueError("Each reviewer must be a string.")
    return [r for r in reviewers if r]

def validate_pr_id(pr_id):
    try:
        pr_id_int = int(pr_id)
        if pr_id_int < 1:
            raise ValueError("PR ID must be a positive integer.")
        return pr_id_int
    except Exception:
        raise ValueError("PR ID must be a positive integer.")