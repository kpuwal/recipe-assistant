import pytest

from services.oven import CONVENTIONAL_MODE, FAN_MODE, extract_oven_settings


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Verwarm de oven voor op 200 graden.", (200, None)),
        ("Verwarm de oven voor op 180 °C.", (180, None)),
        ("Bak 25 minuten op 180°C.", (180, None)),
        ("Verwarm de heteluchtoven voor op 170 graden.", (170, FAN_MODE)),
        ("Verwarm de oven op 180 graden hetelucht.", (180, FAN_MODE)),
        ("Verwarm de oven op 200 graden (boven-onder).", (200, CONVENTIONAL_MODE)),
        ("Boven- en onderwarmte, 190 graden.", (190, CONVENTIONAL_MODE)),
        ("Verwarm de oven voor op 180-200 graden.", (180, None)),
        ("Verwarm de oven voor op 180 tot 200 °C.", (180, None)),
        ("Verwarm de oven voor op 180 graden Celsius.", (180, None)),
        ("Verwarm de oven voor op 220℃.", (220, None)),
        (
            "Verwarm de oven op 200 graden.\nBreng water van 100 graden aan de kook.",
            (200, None),
        ),
        (
            "Verwarm de oven op 200 graden. Bak daarna op 180 graden.",
            (200, None),
        ),
        ("Verwarm de oven op 200 graden.\nGebruik de heteluchtstand.", (200, FAN_MODE)),
        ("Breng 100 graden water aan de kook.", (None, None)),
        ("Laat de boter op kamertemperatuur komen.", (None, None)),
        ("Verwarm de oven op 500 graden.", (None, None)),
        ("200 gram bloem", (None, None)),
        ("Gasstand 6", (None, None)),
        ("Geen temperatuur genoemd.", (None, None)),
        ("", (None, None)),
    ],
)
def test_extract_oven_settings(text, expected):
    assert extract_oven_settings(text) == expected
