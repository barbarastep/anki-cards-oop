import pytest
from anki.loader import TextFileLoader


@pytest.fixture()
def tmp_file(tmp_path):
    path = tmp_path / "test_words.txt"
    path.write_text("hello,привет\n", encoding="utf-8")
    return str(path)


def test_load_words_loads_words_from_comma_separated_values(tmp_file):
    """Метод `load_words` класса `TextFileLoader` должен выполнить
    загрузку слов из файла, путь до которого передан
    при инициализации экземпляра класса `TextFileLoader`.
    """
    loader = TextFileLoader(file_path=tmp_file)
    words = loader.load_words()
    assert words == {"hello": "привет"}


def test_save_words_saves_words_as_comma_separated_values(tmp_path):
    """Метод `save_words` должен сохранять слова в формате слово,перевод."""
    file_path = tmp_path / "saved_words.txt"
    loader = TextFileLoader(file_path=file_path)
    words = {
        "hello": "привет",
        "world": "мир",
    }

    loader.save_words(words)

    assert file_path.read_text(encoding="utf-8") == (
        "hello,привет\n"
        "world,мир\n"
    )


def test_load_words_returns_empty_dict_for_missing_file(tmp_path):
    """Метод `load_words` должен вернуть пустой словарь, если файла нет."""
    loader = TextFileLoader(file_path=tmp_path / "missing.txt")

    assert loader.load_words() == {}
