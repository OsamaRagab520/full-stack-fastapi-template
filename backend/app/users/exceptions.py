class EmailAlreadyRegisteredError(Exception):
    pass


class EmailAlreadyInUseError(Exception):
    pass


class CurrentPasswordIncorrectError(Exception):
    pass


class PasswordUnchangedError(Exception):
    pass


class CannotDeleteSelfError(Exception):
    pass
