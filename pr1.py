import os
import logging
from github import Github
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pull_request(username, token, repo_name, base_branch, head_branch, reviewers):
    """Create a pull request on GitHub, assign reviewers, and return the URL."""
    try:
        g = Github(username, token)
        repo = g.get_repo(f"{username}/{repo_name}")
        
        pr = repo.create_pull(
            title=f"Merge {head_branch} into {base_branch}",
            body="Automated PR created from script.",
            base=base_branch,
            head=head_branch
        )
        
        # Add reviewers to the PR
        if reviewers:
            reviewer_logins = [r.strip() for r in reviewers.split(',') if r.strip()]
            if reviewer_logins:
                pr.create_review_request(reviewers=reviewer_logins)
                logger.info(f"Reviewers {reviewer_logins} assigned to PR {pr.html_url}")
            else:
                logger.warning(f"No valid reviewers provided for PR {pr.html_url}")
        
        pr_url = pr.html_url
        logger.info(f"Pull request created successfully in '{repo_name}': {pr_url}")
        return pr_url
    except Exception as e:
        logger.error(f"Error creating pull request in repository '{repo_name}': {e}")
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
            reviewers = row['reviewers']
            
            if pd.isna(reviewers) or not reviewers.strip():
                logger.error(f"No reviewers provided for repository '{repo_name}'. Skipping PR creation.")
                continue
            
            logger.debug(f"Processing repository: {repo_name}, base_branch: {base_branch}, head_branch: {head_branch}, reviewers: {reviewers}")
            pr_url = create_pull_request(username, token, repo_name, base_branch, head_branch, reviewers)
            if pr_url:
                pr_urls.append({'repo_name': repo_name, 'pr_url': pr_url})
        
        # Save PR URLs to Excel file
        pr_df = pd.DataFrame(pr_urls)
        pr_df.to_excel(output_excel_file, index=False)
        logger.info(f"PR URLs saved to '{output_excel_file}'")
               
    except Exception as e:
        logger.error(f"Error processing Excel file or creating pull requests: {e}")

def main():
    username = os.getenv('USERNAME')
    token = os.getenv('TOKEN')
    excel_file = os.getenv('EXCEL_FILE', 'reponames.xlsx')  # Path to your Excel file
    output_excel_file = os.getenv('OUTPUT_EXCEL_FILE', 'pr_links.xlsx')  # Path to save PR links in Excel
    
    if not username or not token:
        logger.error("USERNAME or TOKEN environment variable not set.")
        return
    
    process_excel_file(username, token, excel_file, output_excel_file)

if __name__ == "__main__":
    main()
