class AuthorizationError(Exception):
    """Raised when a user is not authorized to perform an action or access a resource."""
    pass

class ValidationError(Exception):
    """Raised when input data fails validation checks."""
    pass

class ExtensionsError(Exception):
    """Raised when an unsupported file extension or type is encountered."""
    pass

class BotError(Exception):
    """Raised when an error occurs during the bot's processing or response generation."""
    pass

class NotFoundError(Exception):
    """Generic exception raised when a requested resource is not found."""
    pass

class ChatNotFoundError(Exception):
    """Raised when the specified chat does not exist in the database."""
    pass

class MessageNotFoundError(Exception):
    """Raised when the specified message does not exist in the database."""
    pass