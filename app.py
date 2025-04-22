from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import openai
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

#load_dotenv("api.env")

from pathlib import Path
load_dotenv(dotenv_path=Path("api.env"))



app=FastAPI()

class SummaryInput(BaseModel):
    summaries:Dict[str,str]

def refined_summary(text: str) -> str:
    client=openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response=client.chat.completions.create(
        model="gpt-4-turbo",
         messages=[
            {
                "role": "user",
                "content": f"Rewrite the following privacy policy section using emojis and simple, engaging language:\n\n{text}"
            }
        ],
        max_tokens=150
    )
    return response.choices[0].message.content




@app.post("/refine")
async def refine(input_data: SummaryInput):
    try:
        refined_summaries = {}
        for heading, text in input_data.summaries.items():
            refined = refined_summary(text)  # Call the function once
            # Clean the text to remove extra spaces and newlines
            cleaned_refined_text = refined.replace("\n", " ").strip()
            refined_summaries[heading] = cleaned_refined_text
        return {"refined summary": refined_summaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))