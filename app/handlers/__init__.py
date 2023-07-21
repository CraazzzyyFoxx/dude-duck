from app.models.bot import bot

# from .error_handler import error_handler
# from .order.close import close_order
# from .order.respond import entry_point
#
# from .order.respond.dialogue import respond_order_no_button_dialogue
# from .order.respond.dialogue import order_conversation_dialogue
# from .order.respond.message import respond_order_no_button_message
# from .order.respond.message import order_conversation_message

from .start import start
from ..models import RESPOND_ORDER_CALLBACK, ORDER_CONFIRM_NO_CALLBACK, CONFIRM_ORDER_RESPONSE_CALLBACK, ORDER_CONFIRM_NO_ARBITRARY_CALLBACK

COMMAND_HANDLERS = {
    "start": start,

}


CALLBACK_QUERY_HANDLERS = {
    RESPOND_ORDER_CALLBACK.regex(): entry_point,
    ORDER_CONFIRM_NO_CALLBACK.regex(): respond_order_no_button_dialogue,
    ORDER_CONFIRM_NO_ARBITRARY_CALLBACK.regex(): respond_order_no_button_message,
    CONFIRM_ORDER_RESPONSE_CALLBACK.regex(): close_order
}

for command_name, command_handler in COMMAND_HANDLERS.items():
    application.add_handler(CommandHandler(command_name, command_handler))

for pattern, handler in CALLBACK_QUERY_HANDLERS.items():
    application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

application.add_error_handler(error_handler)
application.add_handler(order_conversation_message)
application.add_handler(order_conversation_dialogue)
