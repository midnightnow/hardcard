import subprocess
import re

def get_projects():
    projects = []
    with open('firebase_projects.txt', 'r') as f:
        for line in f:
            parts = line.split('│')
            if len(parts) > 2:
                pid = parts[2].strip()
                pid = pid.replace('(current)', '').strip()
                if pid and pid != 'Project ID' and '─' not in pid:
                    projects.append(pid)
    return projects

def check_project_for_site(project_id):
    try:
        # Check if site exists using channel list command
        # This will fail if site doesn't exist in project
        cmd = ["firebase", "hosting:channel:list", "--site", "hardcard-world", "--project", project_id]
        print(f"Checking {project_id}...", end="", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f" FOUND! Site hardcard-world belongs to project: {project_id}")
            print("Output:", result.stdout)
            return True
        elif "HTTP Error: 404" in result.stderr or "not found" in result.stderr:
            print(" nope (not found)")
        else:
            err = result.stderr.strip().split('\n')[0]
            print(f" error: {err}")
    except Exception as e:
        print(f" script error: {e}")
    return False

projects = get_projects()
print(f"Scanning {len(projects)} projects for site 'hardcard-world'...")

# Check ALL projects
for p in projects:
    if check_project_for_site(p):
        print("\n!!! SUCCESS !!!")
        break
