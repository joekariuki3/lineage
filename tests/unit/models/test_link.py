import pytest

from app.models.link import Link


def test_link_initialization():
    """
    Test the initialization of a Link instance.
    Verifies that attributes are correctly set.
    """
    link = Link(link="https://joelmuhoho.com", family_id=1)
    assert link.link == "https://joelmuhoho.com"
    assert link.family_id == 1


def test_link_max_url_length_validation():
    """
    Test that Link raises a ValueError when the URL exceeds the maximum length.
    """
    long_url = "a" * (Link.MAX_URL_LENGTH + 1)
    with pytest.raises(ValueError) as excinfo:
        Link(link=long_url, family_id=1)
    assert f"Link URL cannot exceed {Link.MAX_URL_LENGTH} characters" in str(excinfo.value)


def test_link_repr():
    """
    Test the string representation of a Link instance.
    """
    link = Link(link="https://joelmuhoho.com", family_id=1)
    link.link_id = 42  # Simulate setting the ID as would happen in the database
    assert repr(link) == "<Link id=42 family_id=1>"
