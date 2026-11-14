import pytest
from cosmic_astronomy.irsa import build_sia_url


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_coordinates_are_rejected_without_http(value):
    with pytest.raises(ValueError):
        build_sia_url(value, 0, 0.1)


def test_untrusted_collection_is_rejected():
    with pytest.raises(ValueError):
        build_sia_url(0, 0, 0.1, collection="https://untrusted.invalid")
