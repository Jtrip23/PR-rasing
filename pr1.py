import os
import logging
from github import Github, GithubException
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pull_request(username, token, repo_name, base_branch, head_branch, reviewers):
    """Create a pull request on GitHub and assign reviewers."""
    try:
        g = Github(username, token)
        repo = g.get_repo(f"{username}/{repo_name}")
        
        # Create the pull request
        pr = repo.create_pull(
            title=f"Merge {head_branch} into {base_branch}",
            body="Automated PR created from script.",
            base=base_branch,
            head=head_branch
        )
        
        # Assign reviewers if any
        if reviewers:
            reviewers_list = [reviewer.strip() for reviewer in reviewers.split(',')]
            pr.create_review_request(reviewers=reviewers_list)
            logger.info(f"Reviewers assigned: {', '.join(reviewers_list)}")
        
        pr_url = pr.html_url
        logger.info(f"Pull request created successfully in '{repo_name}': {pr_url}")
        return pr_url
    except GithubException as e:
        logger.error(f"GitHub error creating pull request in repository '{repo_name}': {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating pull request in repository '{repo_name}': {e}")
    return None

def process_excel_file(username, token, excel_file, output_excel_file):
    """Process an Excel file to create pull requests and save PR URLs."""
    try:
        if not os.path.isfile(excel_file):
            raise FileNotFoundError(f"The Excel file '{excel_file}' does not exist.")
        
        df = pd.read_excel(excel_file, engine='openpyxl')
        required_columns = {'name', 'base_branch', 'head_branch', 'reviewers'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Excel file must contain columns: {', '.join(required_columns)}")
        
        pr_urls = []
        
        for index, row in df.iterrows():
            repo_name = row['name']
            base_branch = row['base_branch']
            head_branch = row['head_branch']
            reviewers = row.get('reviewers', '')
            logger.debug(f"Processing repository: {repo_name}, base_branch: {base_branch}, head_branch: {head_branch}, reviewers: {reviewers}")
            pr_url = create_pull_request(username, token, repo_name, base_branch, head_branch, reviewers)
            if pr_url:
                pr_urls.append({'repo_name': repo_name, 'pr_url': pr_url})
        
        # Save PR URLs to Excel file
        pr_df = pd.DataFrame(pr_urls)
        pr_df.to_excel(output_excel_file, index=False)
        logger.info(f"PR URLs saved to '{output_excel_file}'")
               
    except FileNotFoundError as e:
        logger.error(e)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(f"Error reading Excel file or creating pull requests: {e}")

if __name__ == "__main__":
    username = os.getenv('USERNAME')
    token = os.getenv('TOKEN')
    excel_file = os.getenv('EXCEL_FILE', 'reponames.xlsx')
    output_excel_file = os.getenv('OUTPUT_EXCEL_FILE', 'pr_links.xlsx')
    
    if not username or not token:
        logger.error("USERNAME or TOKEN environment variable not set.")
    else:
        process_excel_file(username, token, excel_file, output_excel_file)
