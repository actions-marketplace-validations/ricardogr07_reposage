"""Core module."""


class PublicClass:
    """A documented public class."""

    def method(self) -> str:
        return "hello"


def typed_function(x: int) -> str:
    """A typed and documented function."""
    return str(x)


def untyped_function(x):
    return x


def _private_helper(x: int) -> int:
    return x + 1


CONSTANT = "public_constant"
