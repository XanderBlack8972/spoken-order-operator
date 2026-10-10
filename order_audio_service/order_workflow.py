from .models import HeardOrderIntent, OrderAction, OrderState


def decide_order_action(
    order_id: str,
    customer_name: str,
    current_state: OrderState,
    heard: HeardOrderIntent,
) -> OrderAction:
    intent = heard.intent
    next_state = current_state
    needs_review = False

    if intent == "confirm_checkout" and current_state == OrderState.CHECKOUT_PENDING:
        next_state = OrderState.PAID
        action = "capture_checkout"
        update = f"{customer_name}, order {order_id} is paid and ready for fulfillment."
    elif intent == "cancel_order" and current_state in {
        OrderState.CHECKOUT_PENDING,
        OrderState.PAID,
        OrderState.PACKING,
    }:
        next_state = OrderState.CANCELLED
        action = "cancel_before_shipment"
        update = f"{customer_name}, order {order_id} was cancelled before shipment."
    elif intent == "cancel_order":
        needs_review = True
        action = "open_return_review"
        update = f"{customer_name}, order {order_id} has shipped. A return review was opened."
    elif intent == "request_receipt":
        action = "send_receipt"
        update = f"{customer_name}, the receipt for order {order_id} is ready."
    else:
        action = "report_order_state"
        update = f"{customer_name}, order {order_id} is currently {current_state.value}."

    return OrderAction(
        order_id=order_id,
        previous_state=current_state,
        next_state=next_state,
        intent=intent,
        action=action,
        needs_review=needs_review,
        customer_update=update,
    )

