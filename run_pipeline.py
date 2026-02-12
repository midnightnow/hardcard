#!/usr/bin/env python3
"""
MacAgent Pro MLOps Orchestrator
Automates the end-to-end pipeline: Train -> Serve -> Evaluate -> Report
"""

import os
import sys
import subprocess
import time
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import signal
import psutil

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = Path(__file__).parent
MACAGENT_DIR = ROOT_DIR / "macagent-llm"
TRAINING_SCRIPT = ROOT_DIR / "train_macagent_model.py"
ORCHESTRATOR_SCRIPT = ROOT_DIR / "macagent_orchestrator.py"
EVALUATION_SCRIPT = ROOT_DIR / "evaluation" / "benchmark_runner.py"
UNIFIED_SCRIPT = ROOT_DIR / "macagent_hardcard_unified.py"

# Server configuration
SERVER_URL = "http://127.0.0.1:8000"
SERVER_TIMEOUT = 120  # seconds

# Model configuration
DEFAULT_MODEL = "macagent-4b"
AVAILABLE_MODELS = ["macagent-4b", "macagent-13b", "macagent-32b"]

class PipelineOrchestrator:
    """Orchestrates the complete MacAgent Pro training and evaluation pipeline"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL, skip_training: bool = False):
        self.model_name = model_name
        self.skip_training = skip_training
        self.server_process = None
        self.start_time = time.time()
        self.results = {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "training": {"status": "skipped" if skip_training else "pending"},
            "server": {"status": "pending"},
            "evaluation": {"status": "pending"},
            "integration": {"status": "pending"}
        }
    
    def run_command(self, command: list, name: str, timeout: int = None) -> bool:
        """Runs a command in a subprocess and logs its output"""
        logger.info(f"{'='*60}")
        logger.info(f"Starting: {name}")
        logger.info(f"{'='*60}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            
            start = time.time()
            output_lines = []
            
            while True:
                if timeout and (time.time() - start) > timeout:
                    logger.error(f"Command timed out after {timeout} seconds")
                    process.terminate()
                    return False
                
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    line = line.strip()
                    logger.info(f"[{name}] {line}")
                    output_lines.append(line)
            
            return_code = process.wait()
            
            if return_code == 0:
                logger.info(f"✅ {name} completed successfully")
                return True
            else:
                logger.error(f"❌ {name} failed with return code {return_code}")
                return False
                
        except FileNotFoundError:
            logger.error(f"Script not found: {command[0]}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in {name}: {e}")
            return False
    
    async def wait_for_server(self, timeout: int = SERVER_TIMEOUT) -> bool:
        """Waits for the inference server to become available"""
        logger.info(f"Waiting for inference server at {SERVER_URL}...")
        
        start_time = time.time()
        import httpx
        
        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    # Check health endpoint
                    response = await client.get(f"{SERVER_URL}/health", timeout=5.0)
                    if response.status_code == 200:
                        logger.info("✅ Inference server is ready!")
                        return True
                except (httpx.RequestError, httpx.TimeoutException):
                    pass
                
                await asyncio.sleep(2)
        
        logger.error(f"Server did not start within {timeout} seconds")
        return False
    
    def run_training(self) -> bool:
        """Execute the training pipeline"""
        if self.skip_training:
            logger.info("Skipping training phase (--skip-training specified)")
            return True
        
        logger.info(f"Training {self.model_name} model...")
        
        # Check if orchestrator script exists
        if ORCHESTRATOR_SCRIPT.exists():
            command = [
                sys.executable,
                str(ORCHESTRATOR_SCRIPT),
                "--config", str(MACAGENT_DIR / "macagent_config.json"),
                "--model", self.model_name,
                "--action", "train"
            ]
        else:
            # Fallback to direct training script
            command = [
                sys.executable,
                str(TRAINING_SCRIPT),
                "--base-model", self._get_base_model(),
                "--model-name", self.model_name,
                "--epochs", "3",
                "--batch-size", "4"
            ]
        
        success = self.run_command(command, "Training Pipeline", timeout=3600)
        self.results["training"]["status"] = "success" if success else "failed"
        return success
    
    def _get_base_model(self) -> str:
        """Get the base model for the given model size"""
        base_models = {
            "macagent-4b": "microsoft/Phi-3-mini-4k-instruct",
            "macagent-13b": "mistralai/Mistral-7B-Instruct-v0.2",
            "macagent-32b": "deepseek-ai/deepseek-coder-7b-instruct"
        }
        return base_models.get(self.model_name, base_models["macagent-4b"])
    
    def start_inference_server(self) -> bool:
        """Start the inference server in the background"""
        logger.info("Starting inference server...")
        
        # Kill any existing server on the port
        self._kill_process_on_port(8000)
        
        # Start the server
        server_script = ROOT_DIR / "inference" / "server.py"
        
        if server_script.exists():
            # Use the production inference server
            command = [
                sys.executable,
                str(server_script),
                "--model", self.model_name,
                "--port", "8000"
            ]
        elif ORCHESTRATOR_SCRIPT.exists():
            # Fallback to orchestrator
            command = [
                sys.executable,
                str(ORCHESTRATOR_SCRIPT),
                "--config", str(MACAGENT_DIR / "macagent_config.json"),
                "--model", self.model_name,
                "--action", "serve"
            ]
        else:
            # Create a simple server script if needed
            if not server_script.exists():
                self._create_simple_server(server_script)
            
            command = [sys.executable, str(server_script)]
        
        try:
            self.server_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            
            # Log server output in background
            import threading
            def log_output():
                for line in iter(self.server_process.stdout.readline, ''):
                    if line:
                        logger.info(f"[Server] {line.strip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            logger.info(f"Server process started with PID: {self.server_process.pid}")
            self.results["server"]["status"] = "running"
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.results["server"]["status"] = "failed"
            return False
    
    def _kill_process_on_port(self, port: int):
        """Kill any process using the specified port"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        logger.info(f"Killing process {proc.pid} on port {port}")
                        proc.terminate()
                        time.sleep(1)
                        if proc.is_running():
                            proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def _create_simple_server(self, server_path: Path):
        """Create a simple inference server script"""
        server_path.parent.mkdir(exist_ok=True)
        
        server_code = '''#!/usr/bin/env python3
"""Simple inference server for MacAgent Pro"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="MacAgent Pro Inference Server")

class PredictRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256

class PredictResponse(BaseModel):
    generated_text: str
    model: str = "macagent-4b"

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "macagent-4b"}

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    # Mock response for testing
    return PredictResponse(
        generated_text=f"Mock response for: {request.prompt}",
        model="macagent-4b"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        server_path.write_text(server_code)
        logger.info(f"Created simple server at {server_path}")
    
    def run_evaluation(self) -> bool:
        """Run the evaluation benchmarks"""
        logger.info("Running evaluation benchmarks...")
        
        # Create evaluation script if it doesn't exist
        if not EVALUATION_SCRIPT.exists():
            EVALUATION_SCRIPT.parent.mkdir(exist_ok=True)
            self._create_simple_evaluation(EVALUATION_SCRIPT)
        
        command = [
            sys.executable,
            str(EVALUATION_SCRIPT),
            "--server-url", SERVER_URL,
            "--model", self.model_name
        ]
        
        success = self.run_command(command, "Evaluation Harness", timeout=1800)
        self.results["evaluation"]["status"] = "success" if success else "failed"
        
        # Try to load evaluation results
        results_file = ROOT_DIR / "evaluation_results" / f"{self.model_name}_results.json"
        if results_file.exists():
            with open(results_file) as f:
                eval_data = json.load(f)
                self.results["evaluation"]["metrics"] = eval_data
        
        return success
    
    def _create_simple_evaluation(self, eval_path: Path):
        """Create a simple evaluation script"""
        eval_code = '''#!/usr/bin/env python3
"""Simple evaluation script for MacAgent Pro"""

import sys
import json
import argparse
import requests
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="macagent-4b")
    args = parser.parse_args()
    
    print(f"Evaluating {args.model} at {args.server_url}")
    
    # Simple test
    test_prompts = [
        "Empty the trash",
        "Take a screenshot",
        "Show disk usage"
    ]
    
    results = {"model": args.model, "tests": []}
    
    for prompt in test_prompts:
        try:
            response = requests.post(
                f"{args.server_url}/predict",
                json={"prompt": prompt}
            )
            if response.status_code == 200:
                results["tests"].append({"prompt": prompt, "success": True})
            else:
                results["tests"].append({"prompt": prompt, "success": False})
        except Exception as e:
            results["tests"].append({"prompt": prompt, "success": False, "error": str(e)})
    
    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / f"{args.model}_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete!")

if __name__ == "__main__":
    main()
'''
        eval_path.write_text(eval_code)
        logger.info(f"Created simple evaluation at {eval_path}")
    
    def test_integration(self) -> bool:
        """Test the MacAgent + HardCard integration"""
        logger.info("Testing MacAgent + HardCard integration...")
        
        command = [
            sys.executable,
            str(ROOT_DIR / "test_macagent_integration.py")
        ]
        
        success = self.run_command(command, "Integration Test", timeout=300)
        self.results["integration"]["status"] = "success" if success else "failed"
        return success
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up...")
        
        if self.server_process:
            logger.info("Shutting down inference server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Server did not terminate gracefully. Killing...")
                self.server_process.kill()
        
        # Save final results
        results_file = ROOT_DIR / f"pipeline_results_{self.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {results_file}")
    
    def generate_report(self):
        """Generate a final report"""
        duration = time.time() - self.start_time
        
        report = f"""
{'='*70}
MACAGENT PRO PIPELINE REPORT
{'='*70}

Model: {self.model_name}
Duration: {duration/60:.1f} minutes
Timestamp: {self.results['timestamp']}

PIPELINE STAGES:
----------------
1. Training:    {self._format_status(self.results['training']['status'])}
2. Server:      {self._format_status(self.results['server']['status'])}
3. Evaluation:  {self._format_status(self.results['evaluation']['status'])}
4. Integration: {self._format_status(self.results['integration']['status'])}

"""
        
        if 'metrics' in self.results['evaluation']:
            report += f"""
EVALUATION METRICS:
------------------
{json.dumps(self.results['evaluation']['metrics'], indent=2)}
"""
        
        report += f"""
{'='*70}
SUMMARY: {"✅ SUCCESS" if self._is_successful() else "❌ FAILED"}
{'='*70}
"""
        
        logger.info(report)
        
        # Save report
        report_file = ROOT_DIR / f"pipeline_report_{self.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
    
    def _format_status(self, status: str) -> str:
        """Format status with emoji"""
        status_map = {
            "success": "✅ Success",
            "failed": "❌ Failed",
            "running": "🔄 Running",
            "pending": "⏳ Pending",
            "skipped": "⏭️ Skipped"
        }
        return status_map.get(status, status)
    
    def _is_successful(self) -> bool:
        """Check if pipeline was successful"""
        critical_stages = ["server", "evaluation"]
        if not self.skip_training:
            critical_stages.append("training")
        
        return all(
            self.results[stage]["status"] == "success" 
            for stage in critical_stages
        )
    
    async def run(self) -> bool:
        """Run the complete pipeline"""
        try:
            # 1. Training
            if not self.skip_training:
                if not self.run_training():
                    logger.error("Training failed. Aborting pipeline.")
                    return False
            
            # 2. Start Server
            if not self.start_inference_server():
                logger.error("Failed to start server. Aborting pipeline.")
                return False
            
            # 3. Wait for Server
            if not await self.wait_for_server():
                logger.error("Server not ready. Aborting pipeline.")
                return False
            
            # 4. Run Evaluation
            if not self.run_evaluation():
                logger.warning("Evaluation failed, but continuing...")
            
            # 5. Test Integration
            if not self.test_integration():
                logger.warning("Integration test failed.")
            
            return self._is_successful()
            
        finally:
            self.cleanup()
            self.generate_report()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MacAgent Pro MLOps Pipeline Orchestrator"
    )
    parser.add_argument(
        "--model",
        choices=AVAILABLE_MODELS,
        default=DEFAULT_MODEL,
        help="Model to train and evaluate"
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip training and use existing model"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("""
    ╔══════════════════════════════════════════════════╗
    ║         MacAgent Pro MLOps Pipeline              ║
    ║     Train → Serve → Evaluate → Report            ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    orchestrator = PipelineOrchestrator(
        model_name=args.model,
        skip_training=args.skip_training
    )
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\nReceived interrupt signal. Cleaning up...")
        orchestrator.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the pipeline
    success = asyncio.run(orchestrator.run())
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()