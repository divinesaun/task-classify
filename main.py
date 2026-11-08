import os

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

from models import ExtractRequest, ExtractResponse, Extraction, Finding

load_dotenv()

client = OpenAI()
app = FastAPI()

ESCALATE_SIGNS = {"froth_nose_mouth", "unable_to_stand", "cloudy_eye"}

SYSTEM = """Extract livestock signs the farmer actually mentions.

Signs:
- reduced_appetite: eating less, or has stopped eating or grazing
- weakness: dull, weak, lying down more than usual
- swelling: lump below the ear, under the jaw, or in front of the shoulder (mbandabvu)
- rapid_breathing: breathing fast while resting
- cloudy_eye: eye looks white, grey or milky
- froth_nose_mouth: foam or froth from the nose or mouth
- red_urine: urine red, brown, or the colour of strong tea
- unable_to_stand: cannot get up or stay standing
- ticks: ticks can be seen on the animal

Only include mentioned signs. Use not_sure when the farmer sounds unsure.
quote must be copied from the message. English and Shona are both fine
(haisi kudya = not eating, mbandabvu = swelling).
"""


def call_llm(message: str) -> Extraction:
    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": message},
        ],
        text_format=Extraction,
    )
    return response.output_parsed


def decide_escalate(findings: list[Finding]) -> tuple[bool, str]:
    hits = [
        f.sign_id
        for f in findings
        if f.sign_id in ESCALATE_SIGNS and f.value in {"yes", "not_sure"}
    ]
    if not hits:
        return False, "No emergency signs reported."
    return True, f"Emergency sign(s) reported as yes or not_sure: {', '.join(hits)}."


@app.post("/extract")
def extract(body: ExtractRequest) -> ExtractResponse:
    parsed = call_llm(body.message)
    escalate, reason = decide_escalate(parsed.findings)
    return ExtractResponse(findings=parsed.findings, escalate=escalate, reason=reason)
