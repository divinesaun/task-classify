from fastapi.testclient import TestClient

from main import app, decide_escalate
from models import Extraction, Finding

client = TestClient(app)


def test_escalate_on_emergency_yes_or_not_sure():
    escalate, reason = decide_escalate(
        [Finding(sign_id="froth_nose_mouth", value="yes", quote="foam")]
    )
    assert escalate is True
    assert "froth_nose_mouth" in reason

    escalate, _ = decide_escalate(
        [Finding(sign_id="cloudy_eye", value="not_sure", quote="cloudy")]
    )
    assert escalate is True

    escalate, _ = decide_escalate(
        [Finding(sign_id="unable_to_stand", value="no", quote="can stand")]
    )
    assert escalate is False

    escalate, _ = decide_escalate(
        [Finding(sign_id="ticks", value="yes", quote="ticks")]
    )
    assert escalate is False


def test_extract_with_mocked_llm(monkeypatch):
    def fake_llm(message: str) -> Extraction:
        return Extraction(
            findings=[
                Finding(sign_id="reduced_appetite", value="yes", quote="not been eating"),
                Finding(sign_id="rapid_breathing", value="yes", quote="breathing very fast"),
            ]
        )

    monkeypatch.setattr("main.call_llm", fake_llm)
    response = client.post(
        "/extract",
        json={
            "message": "My cow has not been eating since yesterday and she is breathing very fast."
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["escalate"] is False
    assert [f["sign_id"] for f in body["findings"]] == [
        "reduced_appetite",
        "rapid_breathing",
    ]


def test_foam_and_down_escalates(monkeypatch):
    def fake_llm(message: str) -> Extraction:
        return Extraction(
            findings=[
                Finding(
                    sign_id="froth_nose_mouth",
                    value="yes",
                    quote="foam coming from her nose",
                ),
                Finding(sign_id="unable_to_stand", value="yes", quote="she can't get up"),
            ]
        )

    monkeypatch.setattr("main.call_llm", fake_llm)
    response = client.post(
        "/extract",
        json={"message": "There's foam coming from her nose and she can't get up."},
    )
    assert response.json()["escalate"] is True


def test_empty_message_rejected():
    assert client.post("/extract", json={"message": ""}).status_code == 422
