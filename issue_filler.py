import os
import subprocess

import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_ACCESS_TOKEN = os.getenv("GEMINI_ACCESS_TOKEN")


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
            "web_url": f"https://gitlab.ceng.metu.edu.tr/group17/metuapp/-/commit/{commit_hash}",
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
        explanation += f"**Changes:**\n"
        explanation += f"```diff\n{change['diff']}\n```\n\n"
    return explanation


# Function to summarize commit details using Gemini
def summarize_with_gemini(commit_explanations):
    genai.configure(api_key=GEMINI_ACCESS_TOKEN)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = "Your task is to prepare an issue description for the following merge requests. Please review all changes and prepare one task description. The task description should be in the following format:"
    format = """Each of the following items should be a separate short paragraph:

[DEFINITION]

Define the task that you did. [1–2 sentences]
(Example: “I implemented a new feature that allows users to rate the cafeteria menu items.”)

[REASON/PURPOSE]

Why did you need this task in this project? What is the requirement that pushes you to do this task? [1–3 sentences]

[HOW?]

Explain how you did this task.
Itemize each step/action with the following aspects:

	1.	[Setup]
	•	Explain the setup stages (if any)
[1–5 sentences]
	2.	[Data]
	•	Explain the data properties that you use (if any)
[1–2 sentences]
	3.	[Algorithm]
	•	Explain what kind of an algorithm you chose and why (if any)
[1–3 sentences]
	4.	[Tools]
	•	Which technologies/tools did you choose for the development? Specify why it is your preference.
[1 sentence for each tool]
	5.	[Code]
	•	Link the commit: For the commit title use “SPRINT-[X] : [Short and Specific Title]” format.
	6.	[Figures/Charts/Statistics]
	•	It is very important to give some proof indicating your results. This highly affects grading.

[FINAL NOTES]

Specify the final comments. State if the results are sufficient or not. State if there is a new idea/plan coming with this task. [1–3 sentences]"""
    prompt += format
    prompt += "Please do not add any additional text, your response will be directly added as a description to the related issue. Please avoid any expression that will indicate that this is an AI-generated text. The text should indicate that it is written by the same person who did the task."
    for i, commit_explanation in enumerate(commit_explanations):
        prompt += f"\n\nMerge Request {i + 1}:\n\n"
        prompt += commit_explanation + "\n\n"
    response = model.generate_content(prompt)

    return response.text


# Main function
def main():
    # Get commit links from the user
    n = int(input("How many commits do you want to summarize? "))
    commit_hashs = [input(f"Enter commit hash {i + 1}: ").strip() for i in range(n)]

    # Fetch commit details and explanations
    commit_details_list = [get_commit_details(".", hash) for hash in commit_hashs]
    commit_explanations = [
        generate_commit_explanation(details) for details in commit_details_list
    ]

    # Summarize the explanations with Gemini
    summary = summarize_with_gemini(commit_explanations)

    # Print the summary
    print(summary)


if __name__ == "__main__":
    main()
