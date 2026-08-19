import pytest
from anki.anki import Anki


@pytest.mark.parametrize(
    "word, case, expected", [
        (
            "hello",
            "корректных данных",
            "hello"
        ),
        (
            "hello world",
            "отсутствия пробельных символов в начале или конце строки",
            "hello world"
        ),
        (
            "python",
            "корректных данных",
            "python"
        )
    ]
)
def test_normalize_word_method_returns_valid_input_unchanged(word, case,
                                                             expected):
    """Метод `normalize_word` класса `Anki` должен вернуть переданную строку
    неизменённой, если:
     - строка записана в нижнем регистре,
     - в начале и в конце строки нет пробелов.
    """
    assert Anki.normalize_word(word) == expected, (
        "Метод `normalize_word` должен возвращать неизменённую строку,"
        f" если {case}"
    )


@pytest.mark.parametrize(
    "word, expected", [
        ("pYtHoN", "python"),
        ("Hello World", "hello world"),
        ("   Python   ", "python"),
        ("\tHello World\n", "hello world")]
)
def test_normalize_word_method_normalizes_word(word, expected):
    """Метод `normalize_word` класса `Anki` должен
    выполнить нормализацию строки:
        - все символы приведены к нижнему регистру;
        - удалены пробелы в начале и в конце строки.
    """
    assert Anki.normalize_word(word) == expected, (
        "Метод `normalize_word` должен нормализовать"
        " некорректно отформатированные строки."
    )


@pytest.mark.parametrize('invalid_input', [
    1,
    [],
    set(),
])
def test_normalize_word_raises_ValueError_on_invalid_input(invalid_input):
    """Метод `normalize_word` класса `Anki` должен выдавать исключение
    `ValueError`, если в качестве значения параметра `word`
    передана не строка.
    """
    with pytest.raises(ValueError, match='должно быть строкой'):
        Anki.normalize_word(invalid_input)
        pytest.fail(
            "Метод `normalize_word` должен выдавать ValueError"
            " для нестроковых параметров"
        )


@pytest.mark.parametrize("invalid_words", [
    "not a dict",
    [],
    123,
])
def test_anki_init_raises_ValueError_on_invalid_input(invalid_words):
    """Класс `Anki` должен выдавать ValueError, если words не словарь."""
    with pytest.raises(ValueError, match="слов"):
        Anki(words=invalid_words)


@pytest.mark.parametrize("word, translation", [
    (123, "привет"),
    ("hello", 123),
    ([], "привет"),
    ("hello", []),
])
def test_anki_add_word_raises_ValueError_on_invalid_input(word, translation):
    """Метод `add_word` должен выдавать ValueError для нестроковых данных."""
    anki = Anki()

    with pytest.raises(ValueError, match="строк"):
        anki.add_word(word, translation)


def test_get_words_returns_copy():
    """Метод `get_words` должен возвращать копию словаря."""
    anki = Anki(words={"hello": "привет"})
    words = anki.get_words()

    words["python"] = "питон"

    assert anki.get_words() == {"hello": "привет"}


def test_anki_init_normalizes_words():
    """Класс `Anki` должен нормализовать слова при инициализации."""
    anki = Anki(words={"  Hello  ": " ПРИВЕТ "})

    assert anki.get_words() == {"hello": "привет"}
