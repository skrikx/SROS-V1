import os
import subprocess
import re

print("== SROS Apex Sanitizer: Initiating Public Release Scrub ==")

# 1. Identify all tracked files
try:
    tracked_files = subprocess.check_output(["git", "ls-files"]).decode("utf-8").splitlines()
except Exception as e:
    print(f"Error getting tracked files: {e}")
    exit(1)

# Files to untrack
blacklist_patterns = [
    r'\.env$', r'\.env\.local$', r'\.pytest_cache/', r'__pycache__/',
    r'\.pyc$', r'\.log$', r'test_output\.txt$', r'sros_traces\.jsonl$',
    r'sros\.egg-info/', r'apex_commit\.ps1$', r'manual_verify\.py$'
]

def should_untrack(filepath):
    for pattern in blacklist_patterns:
        if re.search(pattern, filepath):
            return True
    return False

# 2. Process Files
files_to_untrack = []
files_to_sanitize = []

for file in tracked_files:
    if should_untrack(file):
        files_to_untrack.append(file)
    elif file.endswith(('.py', '.md', '.yaml', '.yml', '.xml', '.json', '.toml', '.ts', '.js')):
        files_to_sanitize.append(file)

print(f"Found {len(files_to_untrack)} files to untrack.")
if files_to_untrack:
    # chunk the untrack commands to avoid command line limits
    chunk_size = 50
    for i in range(0, len(files_to_untrack), chunk_size):
        chunk = files_to_untrack[i:i + chunk_size]
        subprocess.run(["git", "rm", "-r", "--cached"] + chunk, check=False)

print(f"Scanning {len(files_to_sanitize)} text files for sensitive data...")

# 3. Sanitize content
path_pattern_win = re.compile(r'C:\\[Uu]sers\\hassm\\OneDrive\\Desktop\\SROS', re.IGNORECASE)
path_pattern_unix = re.compile(r'C:/Users/hassm/OneDrive/Desktop/SROS', re.IGNORECASE)
hassm_pattern = re.compile(r'hassm')
api_keys_pattern = re.compile(r'(AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{48})')

changed_files = 0
for filepath in files_to_sanitize:
    if not os.path.isfile(filepath):
        continue
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original = content
        # Replace paths
        content = path_pattern_win.sub('/opt/sros', content)
        content = path_pattern_unix.sub('/opt/sros', content)
        # Replace lone hassm that might remain
        content = hassm_pattern.sub('sros-operator', content)
        # Replace literal secrets
        content = api_keys_pattern.sub('<REDACTED_API_KEY>', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            changed_files += 1
            print(f"Sanitized: {filepath}")
    except Exception as e:
        print(f"Could not read/sanitize {filepath}: {e}")

print(f"Sanitized {changed_files} files.")

# 4. Enforce gitignore
gitignore_additions = """
# Auto-added by Sanitizer
.env
.env.local
.pytest_cache/
__pycache__/
*.pyc
*.log
*.jsonl
test_output.txt
sros.egg-info/
apex_commit.ps1
manual_verify.py
"""
if os.path.isfile('.gitignore'):
    with open('.gitignore', 'r+', encoding='utf-8') as f:
        content = f.read()
        if 'sros.egg-info' not in content:
            f.write(gitignore_additions)
else:
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_additions)
        
print("Appended privacy rules to .gitignore")

# 5. Commit & Push
print("Staging sanitized state and creating commit...")
subprocess.run(["git", "add", "."], check=True)
commit_msg = "SR::Release Preparation::Sanitize Credentials, Caches, and Local Data\n\nApex grade execution: Cleansed local user paths, API keys, dropped non-release files, ignored pycache / envs."
subprocess.run(["git", "commit", "-m", commit_msg], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("== SROS Sanitization and Push Complete ==")
