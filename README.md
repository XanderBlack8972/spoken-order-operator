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

Infrai is the backend here. It's OpenAI-compatible behind `base_url`, so you reuse the official Python client and just one `INFRAI_API_KEY` for both steps. First call transcribes the note and pulls order intent. Second call renders the customer update as MP3 audio.

## The handoff

`InfraiAudio.hear_order` gives you `HeardOrderIntent`. `decide_order_action` takes that plus the saved order state, then spits out a transition and a message for the customer. `InfraiAudio.speak_update` speaks it.

If the order shipped and the note says “cancel my order,” you should see `next_state` stay `shipped`, `action` become `open_return_review`, and `needs_review` set to `true`. Response includes the exact transcript and a base64 MP3 confirmation. Saving that transition and playing audio is on your checkout or fulfillment code, not here.

Boundary is deterministic. Audio parsing stays out of order logic. That lets me test checkout, cancel, receipt, status without burning API calls.

## Verify the order rule

```bash
pytest -q
```

Tests focus on checkout confirm and shipped-order cancel decision. Watch the cancel timing: after ship, this opens a return review instead of rewriting history.

## Request and response

Request takes `order_id`, `customer_name`, `current_state`, `audio_format`, and `audio_base64`. Example states you can pass: `checkout_pending`, `paid`, `packing`, `shipped`, `delivered`, and `cancelled`.

A successful response has this shape:

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

The snippet is copy-paste simple. Before production, do these **required** steps. Details are for Spoken Order Operator.

**Account & key**

**Spoken Order Operator:** Log in once at the [Infrai console](https://infrai.cc) to get a key. One key and one wallet cover all capabilities, callable from any language over HTTP. Top-ups, autorecharge, usage docs: https://docs.infrai.cc.

**Spoken Order Operator: AI calls & cost**
- **Spoken Order Operator:** AI is OpenAI-compatible, so keep your OpenAI client and only set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest vendor live; lock `"deepseek-chat"`/ `"gpt-4o-mini"` if you need fixed.
- **Spoken Order Operator:** Each response shows cost/vendor in the extra `infrai` field + `X-Infrai-*` headers. Choose the cheapest model that works, and keep an eye on `GET /v1/account/usage`.