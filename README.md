# TASK README File

## Run

```bash
uv sync
cp .env.example .env   # add your OPENAI_API_KEY
uv run uvicorn main:app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"message": "There is foam coming from her nose and she cannot get up."}'
```

Tests mock the LLM, so they need no network or API key:

```bash
uv run pytest
```

## Decisions

The model only extracts signs. `client.responses.parse` plus a Pydantic `Extraction` model is the whole LLM path: the SDK returns a typed object, so unknown `sign_id`s and bad values never make it through.

`escalate` is ordinary Python. It is true when `froth_nose_mouth`, `unable_to_stand`, or `cloudy_eye` is `yes` or `not_sure`. That rule is product logic, not something the model should guess, and it is what the tests cover without calling OpenAI.

Only mentioned signs are returned. `not_sure` still escalates on those three signs, because a maybe-cloudy eye is worth a look.

## Measuring accuracy

Label a set of real messages (English, Shona, mixed). Score:

- **Signs:** precision and recall per `sign_id`, especially the three emergency ones
- **Value:** `yes` / `no` / `not_sure` on those signs
- **Quote:** is it actually in the message?
- **Escalate:** treat as a consequence of extraction errors, not a separate model score

Start with the five sample messages, a few healthy-animal negatives, and mixed-language lines like `haisi kudya`.

## With more time

With more time I would have connected this backend to WhatsApp Messaging.

## How I used AI

I used Cursor to write the tests and a portion of this README.md file for this task.
