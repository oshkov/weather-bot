from aiogram.fsm.context import FSMContext

import config


def protected_route(func):
    '''Декоратор для проверки доступа к боту'''

    async def verify(data, state: FSMContext):
        if str(data.from_user.id) not in config.USERS:
            return

        await func(data, state)

    return verify