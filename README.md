# Issue Filler
This is a simple tool to fill in the issue template for your tasks.

## How to use
1. Clone this repository.
2. Create a virtual environment and install the dependencies.
3. Create a .env file and add the following environment variables:
    ```
    GEMINI_ACCESS_TOKEN=your_gemini_access_token
    GITLAB_PROJECT_URL=your_gitlab_project_url
    ```
If you want to use ChatGPT instead of Gemini, you can add the following environment variables:
    ```
    OPENAI_API_KEY=your_openai_api_key
    GITLAB_PROJECT_URL=your_gitlab_project_url
    ```
4. Run the script and answer the questions.
5. The issue explanation will be printed to the terminal window. You can copy and paste it to the issue template.
