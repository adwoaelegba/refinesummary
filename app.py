from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import openai
import os
import requests
from bs4 import BeautifulSoup


app = FastAPI()

# Input model: takes a URL
class URLInput(BaseModel):
    url: str

# HTML Extraction Function
def extraction_function(url: str) -> Dict[str, str]:
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch the URL: {url}")
    content = response.text
    
    soup = BeautifulSoup(content, "html.parser")
    sections = {}
    current_heading = None
    current_text = []

    for elem in soup.find_all(["h1", "h2", "h3", "p"]):
        if elem.name in ["h1", "h2", "h3"]:
            if current_heading:
                sections[current_heading] = " ".join(current_text).strip()
            current_heading = elem.get_text().strip()
            current_text = []
        else:
            current_text.append(elem.get_text().strip())

    if current_heading and current_text:
        sections[current_heading] = " ".join(current_text).strip()

    return sections

# Refining extraction using OpenAI
def refined_summary(text: str) -> str:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following privacy policy section using emojis and simple, engaging language:\n\n{text}"
            }
        ],
        max_tokens=150
    )
    return response.choices[0].message.content

# Main API route
@app.post("/refined")
async def refine_from_url(input_data: URLInput):
    try:
        extracted_sections = extraction_function(input_data.url)

        if not extracted_sections:
            raise HTTPException(status_code=400, detail="No sections extracted from the document.")

        refined_summaries = {}

        for heading, text in extracted_sections.items():
            if not text or text.isspace():
                refined_summaries[heading] = "Sorry, there's nothing to see here."
                continue

            refined = refined_summary(text)
            cleaned = refined.replace("\n", " ").strip()
            refined_summaries[heading] = cleaned

        return {"refined summary": refined_summaries}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
