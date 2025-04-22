from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import openai
import os
from dotenv import load_dotenv

load_dotenv()

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
        refined_summaries={}
        for heading, text in input_data.summaries.items():
            refined=refined_summary(text)
            refined_summaries[heading]=refined
        return{"refined summary": refined_summaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))