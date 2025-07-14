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
