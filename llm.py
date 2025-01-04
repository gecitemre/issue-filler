import os


class LLMBase:
    def __init__(self):
        pass

    def generate_content(self, prompt):
        raise NotImplementedError("Subclasses should implement this method")

    @staticmethod
    def factory(llm_type):
        if llm_type == "chatgpt":
            return ChatGPT()
        if llm_type == "gemini":
            return Gemini()
        raise ValueError("Invalid LLM type")


class ChatGPT(LLMBase):
    def __init__(self):
        import openai

        super().__init__()
        self.model = "gpt-3.5-turbo"
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_content(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.model, messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message["content"]


class Gemini(LLMBase):
    def __init__(self):
        import google.generativeai as genai

        super().__init__()
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        genai.configure(api_key=os.getenv("GEMINI_ACCESS_TOKEN"))

    def generate_content(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text


def get_llm_type():
    if "GEMINI_ACCESS_TOKEN" in os.environ:
        return "gemini"
    elif "OPENAI_API_KEY" in os.environ:
        return "chatgpt"


def prepare_issue_description(commit_explanations):
    llm_type = get_llm_type()
    llm = LLMBase.factory(llm_type)

    task_definition = "Your task is to prepare an issue description for the following merge requests. Please review all changes and prepare one task description. The task description should be in the following format:"
    with open("issue_template.txt", "r") as f:
        issue_template = f.read()
    final_notes = "Please do not add any additional text, your response will be directly added as a description to the related issue. Please avoid any expression that will indicate that this is an AI-generated text. The text should indicate that it is written by the same person who did the task."
    prompt = f"{task_definition}\n\n{issue_template}\n\n{final_notes}"
    for i, commit_explanation in enumerate(commit_explanations):
        prompt += f"\n\nCommit Explanation {i + 1}:\n\n"
        prompt += commit_explanation + "\n\n"

    return llm.generate_content(prompt)
