import copy


class Anki:
    """Класс приложения для тренировки слов."""

    def __init__(self, *, words: dict[str, str] | None = None) -> None:
        if words is None:
            words = {}

        if not isinstance(words, dict):
            raise ValueError("words должен быть словарём")

        self._words: dict[str, str] = {}

        for word, translation in words.items():
            self.add_word(word, translation)

    def get_words(self) -> dict[str, str]:
        """Возвращает копию словаря слов."""
        return copy.copy(self._words)

    @staticmethod
    def normalize_word(word: str) -> str:
        """Нормализует слово."""
        if not isinstance(word, str):
            raise ValueError("word должно быть строкой")

        return word.strip().lower()

    def add_word(self, word: str, translation: str) -> None:
        """Добавляет слово и перевод в словарь."""

        if not isinstance(word, str) or not isinstance(translation, str):
            raise ValueError("word и translation должны быть строками")

        normalized_word = self.normalize_word(word)
        normalized_translation = self.normalize_word(translation)

        self._words[normalized_word] = normalized_translation
