from typing import Iterable


def is_admin(user_id: int, admin_ids: Iterable[int]) -> bool:
    return user_id in set(admin_ids)
