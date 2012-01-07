class FriendlyDBError(Exception):
    pass


class StorageError(FriendlyDBError):
    pass


class ConfigError(FriendlyDBError):
    pass
