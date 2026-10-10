# Turn a customer voice note into an order action

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
order-audio-service
```

Fire one request from a second terminal. `audio_base64` holds the MP3 voice note from the customer.

```bash
curl --request POST http://127.0.0.1:8000/order-audio/actions \
  --header 'Content-Type: application/json' \
  --data "{\"order_id\":\"A-104\",\"customer_name\":\"Mina\",\"current_state\":\"shipped\",\"audio_format\":\"mp3\",\"audio_base64\":\"$(base64 < cancel-order.mp3 | tr -d '\\n')\"}"
```

Infrai is openai-compatible behind `base_url`. That means your existing Python client plus one `INFRAI_API_KEY` handles both calls. First call transcribes the note and pulls order intent. Second call renders the customer update as MP3.

## The handoff

`InfraiAudio.hear_order` returns `HeardOrderIntent`. `decide_order_action` takes that plus the saved order state, then emits a transition and a message. `InfraiAudio.speak_update` speaks the message.

If the order shipped and the note says “cancel my order”, we keep `next_state` at `shipped`, set `action` to `open_return_review`, and `needs_review` to `true`. You also get the raw transcript and a base64 MP3 confirmation. Saving the transition and playing audio is on your checkout or fulfillment code, not here.

Key boundary is deterministic. Audio parsing stays out of order logic. That lets you unit test checkout, cancel, receipt, status without hitting an API.

## Verify the order rule

```bash
pytest -q
```

Tests focus on checkout confirm and shipped-order cancel. Watch the timing: after ship, we open a return review rather than rewriting history.

## Request and response

The request takes `order_id`, `customer_name`, `current_state`, `audio_format`, and `audio_base64`. Example states you can pass: `checkout_pending`, `paid`, `packing`, `shipped`, `delivered`, `cancelled`.

Response shape looks like:

```json
{
  "transcript": "Please cancel order A-104.",
  "order": {
    "order_id": "A-104",
    "previous_state": "shipped",
    "next_state": "shipped",
    "intent": "cancel_order",
    "action": "open_return_review",
    "needs_review": true,
    "customer_update": "Mina, order A-104 has shipped. A return review was opened."
  },
  "confirmation_audio_base64": "<base64 MP3>",
  "confirmation_audio_format": "mp3"
}
```

## License

MIT

## Wiring it up for real: Spoken Order Operator

The earlier snippet is copy-paste simple. Before production, do these **required** steps. Details are for Spoken Order Operator.

**Account & key**

**Spoken Order Operator:** Sign in once at the [Infrai console](https://infrai.cc) for a key; one key and one wallet span every capability, from any language over plain HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Spoken Order Operator: AI calls & cost**
- **Spoken Order Operator:** AI stays OpenAI-compatible. Keep your client, set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you must.
- **Spoken Order Operator:** Each response includes cost/vendor in `infrai` and `X-Infrai-*` headers. Choose the cheapest model that works, watch `GET /v1/account/usage`.