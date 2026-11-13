import pytest

from finanalyzer.text_utils import extract_numbers, number_in_text, parse_ptbr_number, pct_change


@pytest.mark.parametrize("tok,exp", [("1.234.567", 1234567.0), ("12,5", 12.5), ("(1.180)", -1180.0), ("-3,32", -3.32), ("13.75", 13.75)])
def test_parse_ptbr(tok, exp):
    assert parse_ptbr_number(tok) == pytest.approx(exp)


def test_extract_numbers_keeps_multiples_and_percent():
    nums = extract_numbers("alavancagem de 3,32x e Selic de 13.75% com R$ 1.180 mi")
    assert 3.32 in nums and 13.75 in nums and 1180.0 in nums


def test_number_in_text_ignores_sign():
    assert number_in_text(-1180, "EBITDA de R$ 1.180 mi")
    assert not number_in_text(1181, "EBITDA de R$ 1.180 mi")


def test_pct_change():
    assert pct_change(110, 100) == pytest.approx(10.0)
    assert pct_change(1, 0) is None
