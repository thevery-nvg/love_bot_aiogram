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
    return_to_main = 'return_to_main'


class ProfileActions(CallbackData, prefix='#view_action'):
    action: ProfileOptions


user_profile_actions = [
    {'text': 'Смотреть анкеты', 'cb': ProfileActions(action=ProfileOptions.view_people)},
    {'text': 'Мой профиль', 'cb': ProfileActions(action=ProfileOptions.view_my_profile)},
]

freeze = [{'text': 'Заморозить',
           'cb': ProfileActions(
               action=ProfileOptions.freeze_profile)}, ]
unfreeze = [{'text': 'Разморозить',
             'cb': ProfileActions(
                 action=ProfileOptions.unfreeze_profile)}]

viewing_actions = [
    {'text': 'Like👍🏻', 'cb': ProfileActions(action=ProfileOptions.like)},
    {'text': 'Dislike👎🏻', 'cb': ProfileActions(action=ProfileOptions.dislike)},
    {'text': 'Return to main menu', 'cb': ProfileActions(action=ProfileOptions.return_to_main)},
]

user_profile_keyboard = InlineConstructor.create_kb(user_profile_actions + freeze, [1, 2])
user_profile_keyboard_frozen = InlineConstructor.create_kb(user_profile_actions + unfreeze, [1, 2])
viewing_keyboard = InlineConstructor.create_kb(viewing_actions, [2, 1])
