from .generators import add_tos_consents, new_tos_consents


def consent_to_tos(user, tos):
    if tos.role.role == "student":
        add_tos_consents(new_tos_consents(user.student, tos))

    elif tos.role.role == "teacher":
        add_tos_consents(new_tos_consents(user.user, tos))

    else:
        raise NotImplementedError()
