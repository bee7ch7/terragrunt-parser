import git
import os

def get_only_changed_folders(repository_path, branch1, branch2):
    repo = git.Repo(repository_path)
    
    # Get the commit objects for the two branches
    commit1 = repo.commit(branch1)
    commit2 = repo.commit(branch2)

    # Get the list of changed files between two commits
    changed_files = repo.git.diff(commit1, commit2, name_only=True).splitlines()
    filtered_paths = [path for path in changed_files if path.endswith('terragrunt.hcl')]
    result = {"1": [os.path.dirname(path) for path in filtered_paths]}

    return result