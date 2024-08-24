import os
import logging
from github import Github
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pull_request(username, token, repo_name, base_branch, head_branch, reviewers):
    try:
        g = Github(username, token)
        repo = g.get_repo(f"{username}/{repo_name}")
        pr = repo.create_pull(
            title=f"Merge {head_branch} into {base_branch}",
            body="Automated PR created from script.",
            base=base_branch,
            head=head_branch
        )
        logger.info(f"Pull request created successfully in '{repo_name}': {pr.html_url}")

        # Add reviewers to the PR
        if reviewers:
            reviewers_list = [reviewer.strip() for reviewer in reviewers.split(',')]
            repo.get_pull(pr.number).review_requests.create(reviewers=reviewers_list)
            logger.info(f"Reviewers added to PR in '{repo_name}': {', '.join(reviewers_list)}")

    except Exception as e:
        logger.error(f"Error creating pull request in repository '{repo_name}': {e}")

def process_excel_file(username, token, excel_file):
    try:
        df = pd.read_excel(excel_file, engine='openpyxl')
        required_columns = {'name', 'base_branch', 'head_branch', 'reviewers'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Excel file must contain columns: {', '.join(required_columns)}")
        
        for index, row in df.iterrows():
            repo_name = row['name']
            base_branch = row['base_branch']
            head_branch = row['head_branch']
            reviewers = row['reviewers']
            create_pull_request(username, token, repo_name, base_branch, head_branch, reviewers)
    except Exception as e:
        logger.error(f"Error reading Excel file or creating pull requests: {e}")

if __name__ == "__main__":
    username = os.getenv('USERNAME')
    token = os.getenv('TOKEN')
    excel_file = os.getenv('EXCEL_FILE', 'reponames.xlsx')  # Path to your Excel file

    if not username or not token:
        logger.error("USERNAME or TOKEN environment variable not set.")
    else:
        process_excel_file(username, token, excel_file)
