import copy
import random


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
        """Возвращает копию словаря слов.

        Returns:
            dict[str, str]: Копия словаря слов.
        """
        return copy.copy(self._words)

    def get_random_word(self) -> str:
        """Возвращает случайное слово из словаря.

        Returns:
            Случайное слово из словаря.

        Raises:
            ValueError: Если словарь слов пуст.
        """
        if not self._words:
            raise ValueError("Нельзя выбрать слово из пустого словаря")

        return random.choice(list(self._words.keys()))

    def check_translation(self, word: str, translation: str) -> bool:
        """Проверяет перевод слова.

        Args:
            word: Слово, перевод которого нужно проверить.
            translation: Перевод, введённый пользователем.

        Returns:
            True, если перевод корректен, иначе False.

        Raises:
            ValueError: Если word отсутствует в словаре
            или аргументы не строки.
        """
        normalized_word = self.normalize_word(word)
        normalized_translation = self.normalize_word(translation)

        if normalized_word not in self._words:
            raise ValueError("Слово отсутствует в словаре")

        return self._words[normalized_word] == normalized_translation

    def get_translation(self, word: str) -> str:
        """Возвращает перевод слова.

        Args:
            word: Слово, перевод которого нужно получить.

        Returns:
            Перевод слова.

        Raises:
            ValueError: Если word отсутствует в словаре
            или аргумент не строка.
        """
        normalized_word = self.normalize_word(word)

        if normalized_word not in self._words:
            raise ValueError("Слово отсутствует в словаре")

        return self._words[normalized_word]

    @staticmethod
    def normalize_word(word: str) -> str:
        """Нормализует слово.

        Args:
            word: Слово для нормализации.

        Returns:
            Нормализованное слово без пробелов по краям в нижнем регистре.

        Raises:
            ValueError: Если word не является строкой.
        """
        if not isinstance(word, str):
            raise ValueError("word должно быть строкой")

        return word.strip().lower()

    def add_word(self, word: str, translation: str) -> None:
        """Добавляет слово и перевод в словарь.

        Args:
            word: Слово для добавления.
            translation: Перевод слова.

        Returns:
            None

        Raises:
            ValueError: Если word или translation не являются строками.
        """

        if not isinstance(word, str) or not isinstance(translation, str):
            raise ValueError("word и translation должны быть строками")

        normalized_word = self.normalize_word(word)
        normalized_translation = self.normalize_word(translation)

        self._words[normalized_word] = normalized_translation

    def __contains__(self, word: str) -> bool:
        """Проверяет, есть ли слово в словаре.

        Args:
            word: Слово для поиска.

        Returns:
            True, если нормализованное слово есть в словаре, иначе False.

        Raises:
            ValueError: Если word не является строкой.
        """
        normalized_word = self.normalize_word(word)
        return normalized_word in self._words

    def __iter__(self):
        """Возвращает итератор по парам слово-перевод.

        Returns:
            Итератор по парам из словаря слов.
        """
        return iter(self._words.items())

    def __len__(self) -> int:
        """Возвращает количество слов в игре.

        Returns:
            int: Количество слов в словаре.
        """
        return len(self._words)

    def __str__(self) -> str:
        """Возвращает строковое представление объекта Anki.

        Returns:
            Строковое представление объекта Anki.
        """
        return f"Anki: {len(self)} слов"
