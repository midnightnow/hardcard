import subprocess
import re

def get_projects():
    projects = []
    with open('firebase_projects.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Lines are like '│ Project Name │ project-id │ ... │'
            match = re.search(r'│\s*[^│]+\s*│\s*([a-z0-9-]+)\s*│', line)
            if match:
                pid = match.group(1).strip()
                if pid != 'project-id': # Skip header
                    projects.append(pid)
    return projects

def check_project(project_id):
    try:
        # Run hosting:sites:list --project <id>
        # Use grep to speed up searching for hardcard-world
        cmd = ["firebase", "hosting:sites:list", "--project", project_id]
        print(f"Checking {project_id}...", end="", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "hardcard-world" in result.stdout: # Look for the exact SITE ID match
            # Specifically check if the site ID column matches
            lines = result.stdout.splitlines()
            for line in lines:
                if "hardcard-world" in line:
                    parts = [p.strip() for p in line.split('│') if p.strip()]
                    if parts and parts[0] == "hardcard-world":
                        print(f" FOUND! Site hardcard-world is in project: {project_id}")
                        return True
        print(" nope.")
    except Exception as e:
        print(f" Error: {e}")
    return False

projects = get_projects()
# Prioritize known potential projects based on conversation history
priority_projects = [
    "hardcard-firebase-studio",
    "hardcard",
    "hardcard-e107f",
    "hardcard-ai", 
    "hardcard-ai-production",
    "celestia-hardcard-studio",
    "hardcard-main",
    "vetsorcery-prod",
    "alexandria-research", 
    "macagent-production"
]

# Move priority projects to front, removing duplicates
unique_projects = []
seen = set()
for p in priority_projects + projects:
    if p not in seen and p in projects: # Only check if present in list
        unique_projects.append(p)
        seen.add(p)
    elif p not in seen: # Add if not in list, might have been missed by strict regex
        unique_projects.append(p)
        seen.add(p)


for p in unique_projects:
    if check_project(p):
        break
