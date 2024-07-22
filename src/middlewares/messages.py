from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class DeleteLastMsgMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
                        ) -> Any:
        chat_id = data['event_chat']
        bot = data['bot']
        dp = data['dp']
        state = await data['state'].get_data()
        last = state.get('last_msg_id')
        if last:
            try:
                await bot.delete_message(chat_id=chat_id.id, message_id=last)
            except Exception as e:
                dp['aiogram_logger'].debug(f"Error occurred while deleting a message: {e}")
        return await handler(event, data)
