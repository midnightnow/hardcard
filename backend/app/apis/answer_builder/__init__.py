import os
import json
import subprocess
import tempfile
import shutil
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
import uuid # Added comment to force reload
from app.apis.reasoning_modules import LLMCodePlannerInput, LLMCodePlannerOutput, generate_code_modification_plan



# Request model for the endpoint
class RunMvpAnswerBuilderRequest(BaseModel):
    modification_request: Optional[str] = Field(None, description="The high-level request for code generation or modification.")
    initial_code_snippet: Optional[str] = Field(None, description="An initial code snippet to be modified. If None, a new script is generated.")
    numbers_to_square: Optional[List[int]] = Field(None, description="Legacy field for squaring numbers, will be overridden by modification_request.")

from datetime import datetime
from app.libs.memory_service import MemoryType
# Removed: from app.apis.memory_models import CreateMemoryRequest
# Removed: from app.apis.agent_memory import create_memory
from app.libs.firebase_admin_service import get_firestore_client # Added

router = APIRouter()

# --- Manifesto Generator V2 ---
class ManifestoGeneratorV2:
    def get_master_manifesto_code_from_plan(self, plan: List[str]) -> str:
        script_parts = [
            "# master_manifesto_from_plan.py",
            "import json",
            "import os",
            "",
            "def create_artifact(artifact_dir: str, filename: str, data: dict):",
            "    artifact_path = os.path.join(artifact_dir, filename)",
            "    with open(artifact_path, \"w\") as f:",
            "        json.dump(data, f)",
            "    print(f\"Artifact created: {artifact_path}\")",
            "",
            "def main():",
            "    base_artifact_dir = \"output_artifacts\"",
            "    if not os.path.exists(base_artifact_dir):",
            "        os.makedirs(base_artifact_dir)",
            "        print(f\"Created base artifact directory: {base_artifact_dir}\")",
            ""
        ]

        for i, step_description in enumerate(plan):
            # Sanitize step_description for use in a function name
            safe_desc_part = ''.join(filter(str.isalnum, step_description.lower().replace(' ', '_')[:20]))
            step_func_name = f"step_{i+1}_{safe_desc_part}" 
            script_parts.append(f"    # --- Step {i+1}: {step_description} ---")
            script_parts.append(f"    print(f\"Executing: Step {i+1} - {step_description}\")")
            script_parts.append(f"    create_artifact(base_artifact_dir, \"step_{i+1}_artifact.json\", {{ \"step_name\": \"{step_description}\", \"status\": \"placeholder output\" }})")
            script_parts.append("")

        script_parts.extend([
            "    print(\"Manifesto from LLM plan execution completed.\")",
            "",
            "if __name__ == \"__main__\":",
            "    main()",
            ""
        ])
        return "\n".join(script_parts)

    def get_master_manifesto_code(self, numbers_input: Optional[List[int]] = None) -> str:
        # Manifesto with two steps: greeting and squaring numbers
        
        if numbers_input is not None:
            # Ensure it's a Python list literal string, e.g., "[10, 20, 30]"
            script_numbers_assignment = f"sample_numbers = {str(numbers_input)}"
        else:
            script_numbers_assignment = "sample_numbers = [1, 2, 3, 4, 5]" # Default

        code = f"""# master_manifesto_v2.py
import json
import os

# Step 1: Greeting
def greeting_step(artifact_dir: str):
    message = "Hello from the Manifested Thinking Process - V2 Greeting Step!"
    print(message)
    artifact_data = {{\"step_name\": \"greeting\", \"output_message\": message}}
    artifact_path = os.path.join(artifact_dir, \"greeting_artifact.json\")
    with open(artifact_path, \"w\") as f:
        json.dump(artifact_data, f)
    print(f\"Greeting artifact created at {{artifact_path}}\")

# Step 2: Square Numbers
def square_numbers_step(numbers: list, artifact_dir: str):
    print(f\"Executing square_numbers_step with input: {{numbers}}\")
    squared_numbers = [x*x for x in numbers]
    output_artifact_data = {{
        \"step_name\": \"square_numbers\",
        \"original_input\": numbers,
        \"transformed_output\": squared_numbers
    }}
    artifact_path = os.path.join(artifact_dir, \"squared_numbers_artifact.json\")
    with open(artifact_path, \"w\") as f:
        json.dump(output_artifact_data, f)
    print(f\"Squared numbers artifact created at {{artifact_path}}\")

def main():
    base_artifact_dir = \"output_artifacts\"
    if not os.path.exists(base_artifact_dir):
        os.makedirs(base_artifact_dir)
        print(f\"Created base artifact directory: {{base_artifact_dir}}\")

    greeting_step(artifact_dir=base_artifact_dir)
    
    {script_numbers_assignment} # Dynamically inserted here
    square_numbers_step(numbers=sample_numbers, artifact_dir=base_artifact_dir)
    
    print(\"Master Manifesto V2 execution completed.\")

if __name__ == \"__main__\":
    main()
"""
        return code

    def save_manifesto_script(self, code: str, filepath: str):
        with open(filepath, "w") as f:
            f.write(code)
        print(f"Generated manifesto saved to: {filepath}")

# --- Answer Builder Log Payload Model ---
class AnswerBuilderLogPayload(BaseModel):
    run_id: str
    timestamp: str
    manifesto_code: str
    stdout: str
    stderr: Optional[str]
    return_code: int
    artifacts: List[Dict[str, Any]]
    temp_dir_path: str
    # New fields for enhanced logging
    plan: Optional[List[str]] = Field(None, description="The LLM-generated plan, if applicable.")
    modification_request: Optional[str] = Field(None, description="The original modification request, if applicable.")
    initial_code_snippet: Optional[str] = Field(None, description="The initial code snippet provided, if applicable.")

    def get_content_for_type(self, memory_type_enum_val: MemoryType) -> Optional[str]:
        # memory_type_enum_val is an instance of MemoryType enum
        if memory_type_enum_val == MemoryType.RAW:
            return self.model_dump_json()
        elif memory_type_enum_val == MemoryType.CONTEXT:
            # Provide a concise summary for context
            artifact_names = [a.get("step_name", "unknown") for a in self.artifacts]
            return (
                f"Run ID: {self.run_id} completed with code {self.return_code}. "
                f"Stdout captured. Stderr: {'Yes' if self.stderr else 'No'}. "
                f"Artifacts: {', '.join(artifact_names) if artifact_names else 'None'}."
            )
        # No KNOWLEDGE representation for this log type to avoid the original info message
        return None

# --- Sandboxed Execution Engine MVP (Generalized Artifact Collection) ---
class SandboxedExecutionEngineMVP:
    def run_manifesto(self, script_path: str, working_dir: str) -> Dict[str, Any]:
        output_artifacts_collect_dir = os.path.join(working_dir, "output_artifacts")
        
        print(f"Running manifesto: {script_path} in working directory: {working_dir}")
        
        process = subprocess.Popen(
            ["python", os.path.basename(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir,
            text=True
        )
        stdout, stderr = process.communicate()
        
        print("Execution STDOUT:")
        print(stdout)
        if stderr:
            print("Execution STDERR:")
            print(stderr)
        
        collected_artifacts = []
        if os.path.exists(output_artifacts_collect_dir):
            for item_name in os.listdir(output_artifacts_collect_dir):
                item_path = os.path.join(output_artifacts_collect_dir, item_name)
                if os.path.isfile(item_path) and item_name.endswith(".json"):
                    try:
                        with open(item_path, "r") as f:
                            artifact_data = json.load(f)
                            collected_artifacts.append(artifact_data)
                        print(f"Retrieved artifact: {item_name}")
                    except Exception as e:
                        print(f"Error reading artifact {item_name}: {e}")
                        if stderr: # Append to existing stderr
                            stderr += f"\nError reading artifact {item_name}: {e}"
                        else: # Initialize stderr
                            stderr = f"Error reading artifact {item_name}: {e}"
        else:
            print(f"Artifact directory not found at {output_artifacts_collect_dir}")
            
        return {
            "stdout": stdout, 
            "stderr": stderr, 
            "artifacts": collected_artifacts,
            "return_code": process.returncode
        }

# --- API Endpoint ---
class MVPRunResponse(BaseModel):
    stdout: str
    stderr: Optional[str] = None
    artifacts: List[Dict[str, Any]] = []
    return_code: int
    message: str
    manifesto_script_path: Optional[str] = None
    temp_dir_path: str
    memory_id: Optional[str] = None

@router.post("/run-mvp-answer-builder", response_model=MVPRunResponse)
async def run_mvp_answer_builder_endpoint(request: RunMvpAnswerBuilderRequest):
    temp_dir = None
    manifesto_code_for_error_log = "Unavailable (generation failed or happened before error)"
    generated_plan: Optional[LLMCodePlannerOutput] = None # To store the plan

    try:
        temp_dir = tempfile.mkdtemp(prefix="manifesto_run_")
        print(f"Created temporary directory: {temp_dir}")

        generator = ManifestoGeneratorV2()
        manifesto_code = "" # Initialize manifesto_code

        if request.modification_request:
            print(f"Processing modification_request: {request.modification_request}")
            planner_input = LLMCodePlannerInput(
                code_snippet=request.initial_code_snippet if request.initial_code_snippet else "# New script based on request", 
                modification_request=request.modification_request
            )
            generated_plan = generate_code_modification_plan(planner_input)
            print(f"Generated plan: {generated_plan.plan}")
            # TODO: Adapt ManifestoGeneratorV2 to use this plan
            # For now, let's use a placeholder or the old logic if no plan
            # This will be the focus of the next step.
            # manifesto_code = generator.get_master_manifesto_code(numbers_input=request.numbers_to_square)
            # Placeholder for plan-based generation:
            manifesto_code = generator.get_master_manifesto_code_from_plan(generated_plan.plan) 
        elif request.numbers_to_square is not None:
            print("Processing legacy numbers_to_square request.")
            manifesto_code = generator.get_master_manifesto_code(numbers_input=request.numbers_to_square)
        else:
            # Default behavior if no specific request is made
            print("No specific request, using default manifesto.")
            manifesto_code = generator.get_master_manifesto_code()
        
        manifesto_code_for_error_log = manifesto_code
        
        script_filename = "manifesto_master_v2.py"
        if request.modification_request and generated_plan:
            script_filename = "manifesto_from_plan.py"

        manifesto_script_path = os.path.join(temp_dir, script_filename)
        generator.save_manifesto_script(manifesto_code, manifesto_script_path)

        engine = SandboxedExecutionEngineMVP()
        results = engine.run_manifesto(script_filename, working_dir=temp_dir)
        
        memory_id_for_response = None
        try:
            log_payload = AnswerBuilderLogPayload(
                run_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                manifesto_code=manifesto_code,
                stdout=results["stdout"],
                stderr=results["stderr"],
                return_code=results["return_code"],
                artifacts=results["artifacts"],
                temp_dir_path=temp_dir,
                # Add plan to log payload if available
                plan=generated_plan.plan if generated_plan and hasattr(generated_plan, 'plan') else None,
                modification_request=request.modification_request if request.modification_request else None,
                initial_code_snippet=request.initial_code_snippet if request.initial_code_snippet else None
            )
            # memory_request = CreateMemoryRequest(
            #     memory_type=MemoryType.ANSWER_BUILDER_LOG,
            #     payload=log_payload.model_dump(), # Convert Pydantic model to dict
            #     tags=["answer_builder_run", 
            #           "v2_execution", 
            #           "plan_based" if generated_plan else "static_script",
            #           "success" if results["return_code"] == 0 else "failure"],
            # )
            # memory_entry_response = await create_memory(memory_request)
            # memory_id_for_response = memory_entry_response.memory.id

            fb_db_client = get_firestore_client()
            log_doc_ref = fb_db_client.collection("answerBuilderLogs").document() # Create new doc ref for ID
            log_doc_ref.set(log_payload.model_dump()) # Save payload
            memory_id_for_response = log_doc_ref.id

            print(f"Answer Builder V2 run log saved to Firestore collection 'answerBuilderLogs' with ID: {memory_id_for_response}")
        except Exception as mem_e:
            print(f"Error saving Answer Builder run to memory: {mem_e}")
            # Append memory saving error to stderr to make it visible in the response
            mem_error_str = f"Error saving run to memory: {mem_e}"
            if results["stderr"]:
                 results["stderr"] += f"\n{mem_error_str}"
            else:
                results["stderr"] = mem_error_str

        return MVPRunResponse(
            stdout=results["stdout"],
            stderr=results["stderr"],
            artifacts=results["artifacts"],
            return_code=results["return_code"],
            message="MVP Answer Builder V2 run completed.",
            manifesto_script_path=manifesto_script_path,
            temp_dir_path=temp_dir,
            memory_id=memory_id_for_response
        )
    except Exception as e:
        print(f"Critical error during MVP run: {e}")
        import traceback
        stderr_str = f"Critical error during MVP run: {e}\n{traceback.format_exc()}"
        
        memory_id_on_error = None
        try:
            error_log_payload = AnswerBuilderLogPayload(
                run_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                manifesto_code=manifesto_code_for_error_log,
                stdout="",
                stderr=stderr_str,
                return_code=-1, 
                artifacts=[],
                temp_dir_path=str(temp_dir) if temp_dir else "N/A"
            )
            # error_memory_request = CreateMemoryRequest(
            #     memory_type=MemoryType.ANSWER_BUILDER_LOG,
            #     payload=error_log_payload,
            #     tags=["answer_builder_run", "v2_execution", "error_report"],
            # )
            # error_mem_response = await create_memory(error_memory_request)
            # memory_id_on_error = error_mem_response.memory.id

            fb_db_client_err = get_firestore_client()
            err_log_doc_ref = fb_db_client_err.collection("answerBuilderLogs").document()
            err_log_doc_ref.set(error_log_payload.model_dump()) # Save full model
            memory_id_on_error = err_log_doc_ref.id

            print(f"Saved error details to Firestore collection 'answerBuilderLogs' with ID: {memory_id_on_error}")
        except Exception as mem_e_err:
            print(f"CRITICAL: Failed to save error report to memory: {mem_e_err}")

        return MVPRunResponse(
            stdout="", 
            stderr=stderr_str, 
            artifacts=[],
            return_code=-1, 
            message=f"Critical error during MVP run: {e}",
            temp_dir_path=str(temp_dir) if temp_dir else "N/A",
            memory_id=memory_id_on_error
        )
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e_cleanup:
                print(f"Error cleaning up temp directory {temp_dir}: {e_cleanup}")

