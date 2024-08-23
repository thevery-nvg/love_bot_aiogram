from enum import Enum
from aiogram.filters.callback_data import CallbackData

from src.keyboards.base import InlineConstructor


class FacePickerOptions(str, Enum):
    left = 'left'
    right = 'right'


class FacePickerAction(CallbackData, prefix="#face_picker_action"):
    action: FacePickerOptions
    value: int


face_picker_actions = [
    {'text': 'Слева', 'cb': FacePickerAction(action=FacePickerAction(
        action=FacePickerOptions.left), value=3)},
    {'text': 'Справа', 'cb': FacePickerAction(action=FacePickerAction(
        action=FacePickerOptions.right), value=3)},
]
face_picker_kbd = InlineConstructor.create_kb(face_picker_actions, [2, 1])
