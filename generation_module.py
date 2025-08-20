import os
import requests
from config import (
    LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, HF_API_KEY, HF_MODEL,
    OPENROUTER_API_KEY, OPENROUTER_MODEL, ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    LMSTUDIO_API_URL, LMSTUDIO_MODEL
)

try:
    import openai
except ImportError:
    openai = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
except ImportError:
    pipeline = None
    AutoTokenizer = None
    AutoModelForCausalLM = None

class GenerationModule:
    """
    Core generation module for SIA.

    Responsibilities:
    - Generates outputs, responses, or artifacts as specified in the PRD.
    - Utilizes analysis results and memory context to produce relevant content.
    - Interfaces with integration and orchestrator modules for coordinated output.
    """
def __init__(self):
    """
    Initialize the GenerationModule with LLM integration (OpenAI, Hugging Face, OpenRouter, Anthropic, or LM Studio).
    """
    self.llm_provider = LLM_PROVIDER.lower()
    self.openai_model = OPENAI_MODEL
    self.openai_api_key = OPENAI_API_KEY
    self.hf_model = HF_MODEL
    self.hf_api_key = HF_API_KEY
    self.hf_pipe = None
    self.openrouter_api_key = OPENROUTER_API_KEY
    self.openrouter_model = OPENROUTER_MODEL
    self.anthropic_api_key = ANTHROPIC_API_KEY
    self.anthropic_model = ANTHROPIC_MODEL
    self.lmstudio_api_url = LMSTUDIO_API_URL
    self.lmstudio_model = LMSTUDIO_MODEL

    if self.llm_provider == "huggingface" and pipeline and AutoTokenizer and AutoModelForCausalLM:
        # Load Hugging Face pipeline
        self.hf_pipe = pipeline(
            "text-generation",
            model=self.hf_model,
            tokenizer=self.hf_model,
            use_auth_token=self.hf_api_key if self.hf_api_key else None
        )
    # No explicit OpenRouter or LM Studio client needed; handled via requests

    def generate_code(self, analysis_results, memory_context):
        """
        Generate new code based on analysis results and memory context using the configured LLM.
    
        Args:
            analysis_results (dict): Results from the analysis module.
            memory_context (dict): Relevant long-term memory for context.
    
        Returns:
            str: Generated code as a string.
        """
        prompt = self._build_prompt(analysis_results, memory_context)
        if self.llm_provider == "openai" and openai:
            openai.api_key = self.openai_api_key
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful code generation assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.2,
            )
            return response.choices[0].message.content
        elif self.llm_provider == "huggingface" and self.hf_pipe:
            output = self.hf_pipe(prompt, max_new_tokens=256, do_sample=False)
            return output[0]['generated_text']
        elif self.llm_provider == "openrouter" and self.openrouter_api_key and self.openrouter_model:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/",  # OpenRouter requires a referer
                    "X-Title": "SIA Code Generation"
                }
                data = {
                    "model": self.openrouter_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful code generation assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 512,
                    "temperature": 0.2
                }
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                return f"# OpenRouter error: {e}\n"
        elif self.llm_provider == "anthropic" and self.anthropic_api_key and self.anthropic_model:
            try:
                headers = {
                    "x-api-key": self.anthropic_api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                data = {
                    "model": self.anthropic_model,
                    "max_tokens": 512,
                    "temperature": 0.2,
                    "system": "You are a helpful code generation assistant.",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                # Anthropic returns content as a list of blocks; join them if needed
                if "content" in result and isinstance(result["content"], list):
                    return "".join(block.get("text", "") for block in result["content"])
                elif "content" in result and isinstance(result["content"], str):
                    return result["content"]
                else:
                    return "# Anthropic API: Unexpected response format\n"
            except Exception as e:
                return f"# Anthropic error: {e}\n"
        elif self.llm_provider == "lmstudio" and self.lmstudio_api_url and self.lmstudio_model:
            try:
                headers = {
                    "Content-Type": "application/json"
                }
                data = {
                    "model": self.lmstudio_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful code generation assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 512,
                    "temperature": 0.2
                }
                resp = requests.post(
                    self.lmstudio_api_url,
                    headers=headers,
                    json=data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                # LM Studio follows OpenAI format
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                return f"# LM Studio error: {e}\n"
        else:
            return "# Generated code based on analysis and memory context\n"

    def refine_code(self, generated_code, feedback):
        """
        Iteratively refine generated code based on feedback using the configured LLM.
    
        Args:
            generated_code (str): The code to refine.
            feedback (dict): Feedback from tests or analysis.
    
        Returns:
            str: Refined code as a string.
        """
        prompt = self._build_refine_prompt(generated_code, feedback)
        if self.llm_provider == "openai" and openai:
            openai.api_key = self.openai_api_key
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful code refinement assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.2,
            )
            return response.choices[0].message.content
        elif self.llm_provider == "huggingface" and self.hf_pipe:
            output = self.hf_pipe(prompt, max_new_tokens=256, do_sample=False)
            return output[0]['generated_text']
        elif self.llm_provider == "openrouter" and self.openrouter_api_key and self.openrouter_model:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/",
                    "X-Title": "SIA Code Refinement"
                }
                data = {
                    "model": self.openrouter_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful code refinement assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 512,
                    "temperature": 0.2
                }
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                return generated_code + f"\n# OpenRouter error: {e}\n"
        elif self.llm_provider == "anthropic" and self.anthropic_api_key and self.anthropic_model:
            try:
                headers = {
                    "x-api-key": self.anthropic_api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                data = {
                    "model": self.anthropic_model,
                    "max_tokens": 512,
                    "temperature": 0.2,
                    "system": "You are a helpful code refinement assistant.",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                if "content" in result and isinstance(result["content"], list):
                    return "".join(block.get("text", "") for block in result["content"])
                elif "content" in result and isinstance(result["content"], str):
                    return result["content"]
                else:
                    return generated_code + "\n# Anthropic API: Unexpected response format\n"
            except Exception as e:
                return generated_code + f"\n# Anthropic error: {e}\n"
        elif self.llm_provider == "lmstudio" and self.lmstudio_api_url and self.lmstudio_model:
            try:
                headers = {
                    "Content-Type": "application/json"
                }
                data = {
                    "model": self.lmstudio_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful code refinement assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 512,
                    "temperature": 0.2
                }
                resp = requests.post(
                    self.lmstudio_api_url,
                    headers=headers,
                    json=data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                return generated_code + f"\n# LM Studio error: {e}\n"
        else:
            return generated_code + "\n# Refined based on feedback\n"

    def _build_prompt(self, analysis_results, memory_context):
        """
        Build a prompt for code generation from analysis results and memory context.

        Args:
            analysis_results (dict): Results from the analysis module.
            memory_context (dict): Relevant long-term memory for context.

        Returns:
            str: Prompt string.
        """
        return (
            "Generate code based on the following analysis and memory context:\n"
            f"Analysis Results: {analysis_results}\n"
            f"Memory Context: {memory_context}\n"
        )

    def _build_refine_prompt(self, generated_code, feedback):
        """
        Build a prompt for code refinement from generated code and feedback.

        Args:
            generated_code (str): The code to refine.
            feedback (dict): Feedback from tests or analysis.

        Returns:
            str: Prompt string.
        """
        return (
            "Refine the following code based on the feedback provided:\n"
            f"Code:\n{generated_code}\n"
            f"Feedback: {feedback}\n"
        )

    def run_local_tests(self, code_path):
        """
        Run local tests (pytest) on the generated code.
        Args:
            code_path (str): Path to the code or test directory.
        Returns:
            dict: Test results summary.
        """
        import subprocess
        try:
            result = subprocess.run(
                ["pytest", code_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "status": "success" if result.returncode == 0 else "failure",
                "details": result.stdout + "\n" + result.stderr
            }
        except Exception as e:
            return {"status": "error", "details": str(e)}

    def safety_check(self, code):
        """
        Perform safety checks on the generated code using static analysis.
        Args:
            code (str): The code to check.
        Returns:
            dict: Safety check results.
        """
        import ast
        issues = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'eval':
                    issues.append("Use of 'eval' detected")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "imp":
                            issues.append("Use of deprecated library 'imp'")
                if isinstance(node, ast.ImportFrom) and node.module == "imp":
                    issues.append("Use of deprecated library 'imp'")
        except Exception as e:
            return {"safe": False, "issues": [str(e)]}
        return {"safe": len(issues) == 0, "issues": issues}