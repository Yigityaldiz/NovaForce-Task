"""
This script takes an interview transcript and a rubric, uses the OpenAI LLM
to grade the interview, and writes the results to a JSON file.
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from openai import OpenAI, APIError
from dotenv import load_dotenv

# --- CONSTANTS ---
EXTRACTION_MODEL = "gpt-4o"
GRADING_MODEL = "gpt-3.5-turbo"
ANALYSIS_MODEL = "gpt-3.5-turbo"

# --- CORE FUNCTIONS ---


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Grades an interview transcript using an LLM."
    )
    parser.add_argument("--rubric", required=True, help="Path to the rubric JSON file.")
    parser.add_argument(
        "--transcript",
        required=True,
        help="Path to the interview transcript text file.",
    )
    parser.add_argument(
        "--output", required=True, help="Path to write the output analysis JSON file."
    )
    return parser.parse_args()


def setup_api_client() -> OpenAI:
    """Loads API key from .env and sets up the OpenAI client."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not found.", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)


def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Reads a JSON file and returns its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(
            f"ERROR: The file is not a valid JSON: {filepath}",
            file=sys.stderr,
        )
        sys.exit(1)


def load_transcript(filepath: str) -> str:
    """Reads a transcript text file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)


def extract_answers_with_llm(
    client: OpenAI, rubric: List[Dict], transcript: str
) -> Optional[List[Dict]]:
    """Extracts answers for each question from the transcript using an LLM."""
    print("Extracting answers with LLM... (This may take a moment)")

    questions_list = [
        {"id": item["id"], "question_text": item["text"]} for item in rubric
    ]

    system_prompt = """
    Sen bir metin işleme uzmanısın. Görevin, sana verilen bir mülakat transkripti ve bir soru listesini analiz etmektir.
    JSON formatındaki soru listesindeki her bir soru için, adayın transkriptteki cevabını bulup çıkarman gerekiyor.
    Çıktın SADECE ve SADECE aşağıdaki formatta bir JSON objesi olmalıdır. Başka hiçbir metin veya açıklama ekleme.
    {
      "q1_answer": "Adayın 1. soruya verdiği cevap metni...",
      "q2_answer": "Adayın 2. soruya verdiği cevap metni...",
      "q3_answer": "..."
    }
    Eğer bir soruya cevap bulamazsan veya cevap çok kısaysa, değer olarak "Cevap bulunamadı veya yetersiz." yaz.
    """
    user_prompt = f"""
    Soru Listesi (JSON formatında):
    {json.dumps(questions_list, indent=2, ensure_ascii=False)}

    Mülakat Transkripti:
    ---
    {transcript}
    ---
    """

    try:
        response = client.chat.completions.create(
            model=EXTRACTION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        extracted_answers_json = json.loads(response.choices[0].message.content)
        qa_pairs = []
        for item in rubric:
            answer_key = f"{item['id']}_answer"
            answer = extracted_answers_json.get(
                answer_key, "Cevap LLM tarafından bulunamadı."
            )
            qa_pairs.append(
                {
                    "id": item["id"],
                    "text": item["text"],
                    "answer": answer,
                    "rubric_examples": item["examples"],
                }
            )
        print("Answers successfully extracted.")
        return qa_pairs
    except APIError as e:
        print(
            f"ERROR: An OpenAI API error occurred during answer extraction: {e}",
            file=sys.stderr,
        )
        return None
    except json.JSONDecodeError:
        print(
            "ERROR: The response from the LLM for extraction was not valid JSON.",
            file=sys.stderr,
        )
        return None


def grade_single_answer(client: OpenAI, qa_pair: Dict) -> Dict[str, Any]:
    """Grades a single question-answer pair against the rubric."""
    print(f"Grading question {qa_pair['id']}...")
    system_prompt = """
    Sen uzman bir işe alım yöneticisisin. Görevin, bir adayın mülakat sorusuna verdiği cevabı, sağlanan "great", "alright" ve "bad" cevap örneklerine göre değerlendirmektir.
    Değerlendirmenin sonucunda, çıktın SADECE ve SADECE aşağıdaki formatta bir JSON objesi olmalıdır:
    {
      "score": <0 ile 100 arasında bir tam sayı (integer)>,
      "comment": "<Puanı gerekçelendiren 1-2 cümlelik kısa ve profesyonel bir yorum>"
    }
    """
    user_prompt = f"""
    Mülakat Sorusu: {qa_pair['text']}
    ---
    Adayın Cevabı: {qa_pair['answer']}
    ---
    Değerlendirme Kriterleri (Örnek Cevaplar):
    - "great": {qa_pair['rubric_examples']['great']}
    - "alright": {qa_pair['rubric_examples']['alright']}
    - "bad": {qa_pair['rubric_examples']['bad']}
    """
    try:
        response = client.chat.completions.create(
            model=GRADING_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        grade = json.loads(response.choices[0].message.content)
        return grade
    except APIError as e:
        print(
            f"ERROR: An API error occurred while grading question {qa_pair['id']}: {e}",
            file=sys.stderr,
        )
        return {"score": 0, "comment": "An API error occurred during grading."}
    except json.JSONDecodeError:
        print(
            f"ERROR: The grading response for question {qa_pair['id']} was not valid JSON.",
            file=sys.stderr,
        )
        return {"score": 0, "comment": "A format error occurred during grading."}


def generate_overall_analysis(client: OpenAI, results: Dict) -> str:
    """Generates an overall analysis based on all scores and comments."""
    print("Generating overall analysis...")
    system_prompt = "Sen kıdemli bir işe alım direktörüsün. Sana bir mülakattaki sorulara verilen puanlar ve yorumlar sunulacak. Görevin, bu verilere dayanarak adayın genel performansı hakkında kısa, özetleyici ve profesyonel bir analiz paragrafı yazmaktır."
    user_prompt = f"Mülakat Sonuçları:\n{json.dumps(results, indent=2, ensure_ascii=False)}\n\nLütfen bu sonuçlara dayanarak genel bir analiz yaz."
    try:
        response = client.chat.completions.create(
            model=ANALYSIS_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except APIError as e:
        print(
            f"ERROR: An API error occurred during overall analysis generation: {e}",
            file=sys.stderr,
        )
        return "An API error occurred while generating the overall analysis."


def write_output_file(filepath: str, data: Dict):
    """Writes the final results to the specified output file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nAnalysis successfully written to '{filepath}'.")
    except IOError as e:
        print(
            f"ERROR: An I/O error occurred while writing the output file: {e}",
            file=sys.stderr,
        )


def main():
    """Main function to run the interview grading script."""
    args = parse_arguments()
    print("--- Step 1: Initializing and Reading Files ---")
    client = setup_api_client()
    rubric_data = load_json_file(args.rubric)
    transcript_data = load_transcript(args.transcript)
    print("\n--- Step 2: Extracting Question-Answer Pairs ---")
    qa_pairs = extract_answers_with_llm(client, rubric_data, transcript_data)
    if not qa_pairs:
        print(
            "Processing stopped because answers could not be extracted.",
            file=sys.stderr,
        )
        sys.exit(1)
    print("\n--- Step 3: Grading Individual Answers ---")
    graded_results = {}
    total_score = 0
    for pair in qa_pairs:
        grade = grade_single_answer(client, pair)
        graded_results[pair["id"]] = grade
        total_score += grade.get("score", 0)
        time.sleep(1)
    print("\n--- Step 4: Finalizing Results ---")
    overall_score = total_score / len(qa_pairs) if qa_pairs else 0
    overall_analysis = generate_overall_analysis(client, graded_results)
    final_output = {
        "questions": graded_results,
        "overall_score": round(overall_score, 2),
        "overall_analysis": overall_analysis,
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    }
    print("\n--- Step 5: Writing Output File ---")
    write_output_file(args.output, final_output)
    print("\nProcessing complete! ✨")


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    main()
