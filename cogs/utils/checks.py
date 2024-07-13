from typing import List
from discord import Role

class Checks:
    def roles_in_roles(target_roles: List[int], roles: List[Role]) -> bool:
        for role in target_roles:
            for role_ in roles:
                if role == role_.id:
                    return True

                else: continue
        return False