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
    words = anki.words

    words["python"] = "питон"

    assert anki.words == {"hello": "привет"}


def test_anki_init_normalizes_words():
    """Класс `Anki` должен нормализовать слова при инициализации."""
    anki = Anki(words={"  Hello  ": " ПРИВЕТ "})

    assert anki.words == {"hello": "привет"}


def test_get_random_word_returns_word_from_dictionary():
    """Метод `get_random_word` должен возвращать слово из словаря."""
    anki = Anki(words={"hello": "привет"})

    assert anki.get_random_word() == "hello"


def test_get_random_word_raises_ValueError_for_empty_dictionary():
    """Метод `get_random_word` должен выдавать ValueError
    для пустого словаря."""
    anki = Anki()

    with pytest.raises(ValueError, match="пуст"):
        anki.get_random_word()


def test_check_translation_returns_true_for_correct_translation():
    """Метод `check_translation` должен вернуть True для верного перевода."""
    anki = Anki(words={"hello": "привет"})

    assert anki.check_translation("HELLO", " ПРИВЕТ ") is True


def test_check_translation_returns_false_for_wrong_translation():
    """Метод `check_translation` должен вернуть False
    для неверного перевода."""
    anki = Anki(words={"hello": "привет"})

    assert anki.check_translation("hello", "мир") is False


def test_check_translation_raises_ValueError_for_unknown_word():
    """Метод `check_translation` должен выдавать ValueError
    для неизвестного слова."""
    anki = Anki(words={"hello": "привет"})

    with pytest.raises(ValueError, match="отсутств"):
        anki.check_translation("world", "мир")


def test_get_translation_returns_translation_for_existing_word():
    """Метод `get_translation` должен возвращать перевод слова."""
    anki = Anki(words={"hello": "привет"})

    assert anki.get_translation(" HELLO ") == "привет"


def test_get_translation_raises_ValueError_for_unknown_word():
    """Метод `get_translation` должен выдавать ValueError
    для неизвестного слова."""
    anki = Anki(words={"hello": "привет"})

    with pytest.raises(ValueError, match="отсутств"):
        anki.get_translation("world")
