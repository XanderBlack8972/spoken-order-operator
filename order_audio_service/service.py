import base64
import binascii

from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError

from .infrai_audio import InfraiAudio
from .models import OrderAudioRequest, OrderAudioResponse
from .order_workflow import decide_order_action

app = FastAPI(title="Spoken order operator", version="0.1.0")


@app.post("/order-audio/actions", response_model=OrderAudioResponse)
def act_on_order_audio(request: OrderAudioRequest) -> OrderAudioResponse:
    try:
        audio = base64.b64decode(request.audio_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail="audio_base64 must be valid base64") from exc

    try:
        ai = InfraiAudio()
        heard = ai.hear_order(audio, request.audio_format.value)
        action = decide_order_action(
            request.order_id,
            request.customer_name,
            request.current_state,
            heard,
        )
        confirmation = ai.speak_update(action.customer_update)
    except APIStatusError as exc:
        status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=status, detail="Audio request was rejected") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="Could not reach the audio service") from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=502, detail="Unexpected audio response") from exc

    return OrderAudioResponse(
        transcript=heard.transcript,
        order=action,
        confirmation_audio_base64=base64.b64encode(confirmation).decode("ascii"),
    )

