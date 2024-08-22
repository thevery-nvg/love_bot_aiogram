from enum import Enum
from aiogram.filters.callback_data import CallbackData

from src.keyboards.base import InlineConstructor


class ProfileOptions(str, Enum):
    view_people = 'view_people'
    view_my_profile = 'view_my_profile'
    freeze_profile = 'freeze_profile'
    unfreeze_profile = 'unfreeze_profile'
    like = 'like'
    dislike = 'dislike'
    return_to_main_menu = 'return_to_main_menu'
    refill_profile = 'refill_profile'
    update_location = 'update_location'
    face_picker = 'face_picker'


class ProfileAction(CallbackData, prefix='#view_action'):
    action: ProfileOptions
    value: int


user_profile_actions = [
    {'text': 'Смотреть анкеты', 'cb': ProfileAction(action=ProfileOptions.view_people, value=2)},
    {'text': 'Лицемер', 'cb': ProfileAction(action=ProfileOptions.face_picker, value=2)},
    {'text': 'Мой профиль', 'cb': ProfileAction(action=ProfileOptions.view_my_profile, value=2)},
]

freeze = {'text': 'Заморозить',
          'cb': ProfileAction(action=ProfileOptions.freeze_profile, value=2)}
unfreeze = {'text': 'Разморозить',
            'cb': ProfileAction(action=ProfileOptions.unfreeze_profile, value=2)}

viewing_actions = [
    {'text': 'Like👍🏻', 'cb': ProfileAction(action=ProfileOptions.like, value=2)},
    {'text': 'Dislike👎🏻', 'cb': ProfileAction(action=ProfileOptions.dislike, value=2)},
    {'text': 'Return to main menu',
     'cb': ProfileAction(action=ProfileOptions.return_to_main_menu, value=2)},
]
return_to_main_menu = {'text': 'Return to main menu',
                       'cb': ProfileAction(action=ProfileOptions.return_to_main_menu, value=2)}
my_profile_actions = [
    {'text': 'Refill profile', 'cb': ProfileAction(action=ProfileOptions.refill_profile, value=2)},
    {'text': 'Update location',
     'cb': ProfileAction(action=ProfileOptions.update_location, value=2)},
    freeze,
    return_to_main_menu
]


def my_profile_keyboard(frozen: bool):
    if frozen:
        my_profile_actions[2] = unfreeze
    else:
        my_profile_actions[2] = freeze
    return InlineConstructor.create_kb(my_profile_actions, [1, 1, 1, 1])


continue_actions = [{
    'text': 'Продолжить', 'cb': ProfileAction(action=ProfileOptions.view_people, value=2)
}]
user_profile_keyboard = InlineConstructor.create_kb(user_profile_actions, [1, 1])
viewing_keyboard = InlineConstructor.create_kb(viewing_actions, [2, 1])
continue_keyboard = InlineConstructor.create_kb(continue_actions, [1, 1])
