from example_pkg.service import greet


def test_greet() -> None:
    assert greet("team") == "hello team"
