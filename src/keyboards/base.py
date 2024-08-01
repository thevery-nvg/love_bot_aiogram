from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackGame,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LoginUrl,
)

from typing import Sequence, TypeVar, Type

T = TypeVar("T")
A = TypeVar("A", bound=Type[CallbackData])


class InlineConstructor:
    aliases = {"cb": "callback_data"}
    available_properties = [
        "text",
        "callback_data",
        "url",
        "login_url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
        "pay",
    ]
    properties_amount = 1

    @staticmethod
    def create_keyboard_layout(buttons: Sequence[T], count: Sequence[int]) -> list[list[T]]:
        if sum(count) != len(buttons):
            raise ValueError("Количество кнопок не совпадает со схемой")
        temp_list: list[list[T]] = []
        btn_number = 0
        for a in count:
            temp_list.append([])
            for _ in range(a):
                temp_list[-1].append(buttons[btn_number])
                btn_number += 1
        return temp_list

    @staticmethod
    def create_kb(
            actions: list[dict[str, str | bool | A | LoginUrl | CallbackGame,]],
            schema: list[int],
    ) -> InlineKeyboardMarkup:

        buttons: list[InlineKeyboardButton] = []
        # noinspection DuplicatedCode
        for action in actions:
            data: dict[str, str | bool | A | LoginUrl | CallbackGame,] = {}

            for alias, value in InlineConstructor.aliases.items():
                if alias in action:
                    action[value] = action[alias]
                    del action[alias]

            for key in action:
                if key in InlineConstructor.available_properties:
                    if len(data) < InlineConstructor.properties_amount:
                        data[key] = action[key]
                    else:
                        break

            if "callback_data" in data:
                if isinstance(data["callback_data"], CallbackData):
                    data["callback_data"] = data["callback_data"].pack()

            if "pay" in data:
                if len(buttons) != 0 and data["pay"]:
                    raise ValueError("Платежная кнопка должна идти первой в клавиатуре")
                data["pay"] = action["pay"]

            if len(data) < InlineConstructor.properties_amount:
                raise ValueError("Недостаточно данных для создания кнопки")

            buttons.append(InlineKeyboardButton(**data))  # type: ignore

        kb = InlineKeyboardMarkup(
            inline_keyboard=InlineConstructor.create_keyboard_layout(buttons, schema)
        )

        return kb
