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


def prepare_issue_description(commit_explanations, llm_type):
    llm = LLMBase.factory(llm_type)

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

    1.    [Setup]
    •    Explain the setup stages (if any)
[1–5 sentences]
    2.    [Data]
    •    Explain the data properties that you use (if any)
[1–2 sentences]
    3.    [Algorithm]
    •    Explain what kind of an algorithm you chose and why (if any)
[1–3 sentences]
    4.    [Tools]
    •    Which technologies/tools did you choose for the development? Specify why it is your preference.
[1 sentence for each tool]
    5.    [Code]
    •    Link the commit: For the commit title use “SPRINT-[X] : [Short and Specific Title]” format.
    6.    [Figures/Charts/Statistics]
    •    It is very important to give some proof indicating your results. This highly affects grading.

[FINAL NOTES]

Specify the final comments. State if the results are sufficient or not. State if there is a new idea/plan coming with this task. [1–3 sentences]"""
    prompt += format
    prompt += "Please do not add any additional text, your response will be directly added as a description to the related issue. Please avoid any expression that will indicate that this is an AI-generated text. The text should indicate that it is written by the same person who did the task."
    for i, commit_explanation in enumerate(commit_explanations):
        prompt += f"\n\nMerge Request {i + 1}:\n\n"
        prompt += commit_explanation + "\n\n"

    return llm.generate_content(prompt)
