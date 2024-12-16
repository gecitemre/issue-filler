import os
import subprocess

from dotenv import load_dotenv

from llm import prepare_issue_description

load_dotenv()

GEMINI_ACCESS_TOKEN = os.getenv("GEMINI_ACCESS_TOKEN")
GITLAB_PROJECT_URL = os.getenv("GITLAB_PROJECT_URL")
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH")


def get_commit_details(repo_path, commit_hash):
    # Change to the repository directory
    try:
        # Get the commit message (title is the first line)
        commit_message = subprocess.check_output(
            ["git", "-C", repo_path, "log", "--format=%B", "-n", "1", commit_hash],
            text=True,
        ).strip()

        # Get the diffs for the commit
        diff_output = subprocess.check_output(
            ["git", "-C", repo_path, "diff", f"{commit_hash}~1", commit_hash], text=True
        )

        # Split the diff by file for clarity (optional, parse further if needed)
        diff_details = [{"new_path": None, "diff": diff_output}]

        return {
            "diffs": diff_details,
            "title": commit_message.split("\n")[0],  # First line of the commit message
            "web_url": f"{GITLAB_PROJECT_URL}/-/commit/{commit_hash}",
        }
    except subprocess.CalledProcessError as e:
        print(f"Error fetching commit details: {e}")
        return None


# Function to generate commit explanation
def generate_commit_explanation(commit_details):
    explanation = "### Commit Explanation\n\n"
    explanation += f"**Title:** {commit_details['title']}\n\n"
    explanation += f"**Commit Link:** {commit_details['web_url']}\n\n"
    for change in commit_details["diffs"]:
        explanation += f"**File:** {change['new_path']}\n"
        explanation += "**Changes:**\n"
        explanation += f"```diff\n{change['diff']}\n```\n\n"
    return explanation


# Main function
def main():
    # Get commit links from the user
    n = int(input("How many commits do you want to summarize? "))
    commit_hashes = [input(f"Enter commit hash {i + 1}: ").strip() for i in range(n)]

    # Fetch commit details and explanations
    commit_details_list = [
        get_commit_details(GIT_REPO_PATH, hash) for hash in commit_hashes
    ]
    commit_explanations = [
        generate_commit_explanation(details) for details in commit_details_list
    ]

    # Print the summary
    print(prepare_issue_description(commit_explanations))


if __name__ == "__main__":
    main()
