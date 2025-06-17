import zipfile
import requests


def _download_zip_repo(repo_url, temp_dir, owner, repo, session, github_token=None):
    """Fallback method: Download repository as ZIP file"""
    
    # For private repos, use GitHub API zipball endpoint
    if github_token:
        # First, get the default branch
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        api_response = session.get(api_url)
        if api_response.status_code == 200:
            repo_info = api_response.json()
            default_branch = repo_info.get('default_branch', 'main')
        else:
            default_branch = 'main'
        
        # Use API zipball endpoint for private repos
        zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{default_branch}"
    else:
        # Use public download URL for public repos
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
    
    response = session.get(zip_url)
    
    if response.status_code == 404:
        # Try master branch if main doesn't exist
        if github_token:
            zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/master"
        else:
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
        response = session.get(zip_url)
    
    if response.status_code != 200:
        if response.status_code == 404:
            raise Exception(f"Repository not found or no access. Status: {response.status_code}")
        else:
            raise Exception(f"Failed to download repository: {response.status_code}")
    
    # Save and extract the zip file
    zip_path = temp_dir / f"{repo}.zip"
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Find the extracted directory
    # For GitHub API zipballs, the format is usually: owner-repo-commit_sha
    # For regular downloads, it's usually: repo-branch_name
    extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir() and d.name != "__MACOSX__"]
    
    if not extracted_dirs:
        # List all items in temp_dir for debugging
        all_items = list(temp_dir.iterdir())
        print(f"Debug: Items in temp directory: {[item.name for item in all_items]}")
        raise Exception("Could not find extracted repository directory")
    
    # If multiple directories, try to find the most likely one
    if len(extracted_dirs) > 1:
        # Prefer directories that contain the repo name
        repo_candidates = [d for d in extracted_dirs if repo.lower() in d.name.lower()]
        if repo_candidates:
            extracted_dirs = repo_candidates
    
    return extracted_dirs[0]
    
