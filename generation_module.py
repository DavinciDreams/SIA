import os
from config import LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, HF_API_KEY, HF_MODEL

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
        Initialize the GenerationModule with LLM integration (OpenAI or Hugging Face).
        """
        self.llm_provider = LLM_PROVIDER.lower()
        self.openai_model = OPENAI_MODEL
        self.openai_api_key = OPENAI_API_KEY
        self.hf_model = HF_MODEL
        self.hf_api_key = HF_API_KEY
        self.hf_pipe = None

        if self.llm_provider == "huggingface" and pipeline and AutoTokenizer and AutoModelForCausalLM:
            # Load Hugging Face pipeline
            self.hf_pipe = pipeline(
                "text-generation",
                model=self.hf_model,
                tokenizer=self.hf_model,
                use_auth_token=self.hf_api_key if self.hf_api_key else None
            )

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