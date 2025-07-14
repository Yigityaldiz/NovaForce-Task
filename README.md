# Interview Grader CLI (AI-Powered Interview Assessment Tool)

This is a command-line tool that uses a large language model (LLM) to grade an interview transcript against a provided rubric of example answers.

## Features

- **LLM-Powered Parsing**: Intelligently extracts question-answer pairs from various transcript formats.
- **Rubric-Based Grading**: Evaluates each answer against "great," "alright," and "bad" examples.
- **Quantitative & Qualitative Feedback**: Generates a numerical score (0-100) and a qualitative comment for each question.
- **Overall Analysis**: Provides a final aggregated score and a summary analysis of the candidate's performance.
- **JSON Output**: Writes the complete analysis to a structured JSON file with a timestamp.

---

## Requirements

- Python 3.7+
- An OpenAI API Key

---

## ⚙️ Setup & Installation

Follow these steps to set up and run the project locally.

**1. Clone the Repository**

```bash
git clone <your-repository-url>
cd interview-grader
```

**2. Create and Activate a Virtual Environment**

It is highly recommended to use a virtual environment to manage project dependencies.

- **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

**3. Install Dependencies**

This project's dependencies are listed in the `requirements.txt` file. Install them with a single command:

```bash
pip install -r requirements.txt
```

**4. Set Up Environment Variables**

The script requires an OpenAI API key to function.

- Create a file named `.env` in the root of the project folder.
- Add your API key to this file in the following format:
  ```
  OPENAI_API_KEY="your-secret-api-key-goes-here"
  ```
- **Important**: The `.gitignore` file is already configured to ignore `.env`, so your secret key will not be committed to Git.

---
## 🐛 Troubleshooting: `ModuleNotFoundError`

Sometimes, even after activating the `venv` virtual environment and installing packages with `pip install`, you might encounter an error like **`ModuleNotFoundError: No module named 'openai'`** when you run the code.

This usually happens because your IDE (especially Visual Studio Code) hasn't automatically detected the project's virtual environment. The IDE continues to use your system's global Python interpreter, which doesn't have the required packages installed, leading to the error.

**Solution (for Visual Studio Code):**

You need to manually point the IDE to the correct Python interpreter.

1.  **Open the Command Palette:**
    * **macOS:** `Cmd + Shift + P`
    * **Windows/Linux:** `Ctrl + Shift + P`

2.  In the search box that appears, type **`Python: Select Interpreter`** and click the option.

3.  From the list, select the Python interpreter that includes your virtual environment (`venv`). The path will typically contain `./venv/bin/python` and be labeled with `('.venv': venv)`.

4.  After making this selection, restart your IDE or the terminal within the IDE to be safe. This ensures the IDE recognizes the correct environment and can find the libraries.
---

## 🚀 Usage

The script is run from the command line with three required arguments: `--rubric`, `--transcript`, and `--output`.

```bash
python grade_interview.py \
  --rubric path/to/your/rubric.json \
  --transcript path/to/your/interview.txt \
  --output path/to/your/analysis.json
```

### Arguments

- `--rubric`: Path to the rubric JSON file. An example is provided in the repository.
- `--transcript`: Path to the interview transcript text file. Several examples are provided.
- `--output`: Path where the analysis JSON will be written.

### Example

To run the tool with the provided sample files:

```bash
python grade_interview.py --rubric rubric.json --transcript transcript1.txt --output analysis.json
```

The script will print its progress to the console and create the `analysis.json` file with the final report upon completion.

### Inspecting the Output

To view the generated `analysis.json` file in a clean, colorized, and readable format directly in your terminal, you can use the `jq` command-line tool.

```bash
cat analysis.json | jq
```
