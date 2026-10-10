from enum import StrEnum

from pydantic import BaseModel, Field


class AudioFormat(StrEnum):
    MP3 = "mp3"
    WAV = "wav"


class OrderState(StrEnum):
    CHECKOUT_PENDING = "checkout_pending"
    PAID = "paid"
    PACKING = "packing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderIntent(StrEnum):
    CONFIRM_CHECKOUT = "confirm_checkout"
    CANCEL_ORDER = "cancel_order"
    REQUEST_RECEIPT = "request_receipt"
    GET_UPDATE = "get_update"


class OrderAudioRequest(BaseModel):
    order_id: str = Field(min_length=1, max_length=80)
    customer_name: str = Field(min_length=1, max_length=120)
    current_state: OrderState
    audio_base64: str = Field(min_length=1)
    audio_format: AudioFormat


class HeardOrderIntent(BaseModel):
    transcript: str
    intent: OrderIntent


class OrderAction(BaseModel):
    order_id: str
    previous_state: OrderState
    next_state: OrderState
    intent: OrderIntent
    action: str
    needs_review: bool
    customer_update: str


class OrderAudioResponse(BaseModel):
    transcript: str
    order: OrderAction
    confirmation_audio_base64: str
    confirmation_audio_format: str = "mp3"

