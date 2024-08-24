import os
from github import Github
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_pr(username, token, repo_name, base_branch, new_branch_name, pr_title, pr_body, reviewers):
    try:
        g = Github(username, token)
        repo = g.get_repo(f"{username}/{repo_name}")

        # Check if the branch exists
        try:
            repo.get_branch(new_branch_name)
        except Exception as e:
            logging.error(f"Branch '{new_branch_name}' does not exist in repository '{repo_name}': {e}")
            return

        # Create a pull request
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=new_branch_name,
            base=base_branch
        )
        logging.info(f"Pull request created successfully: {pr.html_url}")

        # Add reviewers
        repo.request_reviewers(pr.number, reviewers)
        logging.info(f"Reviewers {reviewers} added to pull request.")

    except Exception as e:
        logging.error(f"Error creating PR in '{repo_name}': {e}")

def create_prs_from_excel(username, token, excel_file):
    try:
        df = pd.read_excel(excel_file, engine='openpyxl')

        # Hardcoded reviewers
        reviewers = ['reviewer1', 'reviewer2']  # Replace with actual GitHub usernames

        for index, row in df.iterrows():
            repo_name = row['name']
            base_branch = row['base_branch']
            new_branch_name = row['new_branch']
            pr_title = row['pr_title'] if 'pr_title' in row else 'New Pull Request'
            pr_body = row['pr_body'] if 'pr_body' in row else 'Please review the changes.'

            create_pr(username, token, repo_name, base_branch, new_branch_name, pr_title, pr_body, reviewers)
    
    except Exception as e:
        logging.error(f"Error reading Excel file or creating PRs: {e}")

if __name__ == "__main__":
    username = os.getenv('USERNAME')
    token = os.getenv('TOKEN')
    excel_file = 'repositories.xlsx'  # Path to your Excel file

    if not username or not token:
        raise ValueError("GitHub username or token not set in environment variables.")
    
    create_prs_from_excel(username, token, excel_file)
