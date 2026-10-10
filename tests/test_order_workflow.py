from order_audio_service.models import HeardOrderIntent, OrderIntent, OrderState
from order_audio_service.order_workflow import decide_order_action


def test_shipped_order_cancellation_opens_return_review() -> None:
    heard = HeardOrderIntent(
        transcript="Please cancel order A-104.",
        intent=OrderIntent.CANCEL_ORDER,
    )

    action = decide_order_action(
        order_id="A-104",
        customer_name="Mina",
        current_state=OrderState.SHIPPED,
        heard=heard,
    )

    assert action.next_state == OrderState.SHIPPED
    assert action.action == "open_return_review"
    assert action.needs_review is True
    assert "has shipped" in action.customer_update


def test_checkout_confirmation_moves_order_to_paid() -> None:
    heard = HeardOrderIntent(
        transcript="Yes, place my order.",
        intent=OrderIntent.CONFIRM_CHECKOUT,
    )

    action = decide_order_action(
        order_id="A-105",
        customer_name="Mina",
        current_state=OrderState.CHECKOUT_PENDING,
        heard=heard,
    )

    assert action.next_state == OrderState.PAID
    assert action.action == "capture_checkout"
    assert action.needs_review is False

