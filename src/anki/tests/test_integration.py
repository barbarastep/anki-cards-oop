from anki.anki import Anki
from anki.loader import TextFileLoader


def test_integration(tmp_path):
    """Проверяет полный сценарий загрузки, изменения и сохранения слов."""
    file_path = tmp_path / "words.txt"
    file_path.write_text(
        "hello,привет\n"
        "world,мир\n",
        encoding="utf-8",
    )

    loader = TextFileLoader(file_path=file_path)
    words = loader.load_words()

    anki = Anki(words=words)

    assert anki.get_words() == {
        "hello": "привет",
        "world": "мир",
    }

    anki.add_word("Python", "Питон")
    loader.save_words(anki.get_words())

    assert file_path.read_text(encoding="utf-8") == (
        "hello,привет\n"
        "world,мир\n"
        "python,питон\n"
    )
