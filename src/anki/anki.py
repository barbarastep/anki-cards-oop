import copy
import random
import time
from collections.abc import Iterator


class Anki:
    """Хранит словарь слов и управляет логикой тренировки."""

    def __init__(self, *, words: dict[str, str] | None = None) -> None:
        """Инициализирует игру со словарём слов.

        Args:
            words: Начальный словарь слов и переводов. Если не передан,
                используется пустой словарь.

        Raises:
            ValueError: Если words не является словарём со строковыми
                ключами и значениями.
        """
        if words is None:
            words = {}

        self._words: dict[str, str] = self._normalize_dict(words)
        self._session_active: bool = False
        self._session_start_time: float = 0.0
        self._session_user_score: int = 0
        self._last_word: str | None = None
        self.last_session_stats: dict[str, int | float] = {
            "correct_answers": 0,
            "total_time": 0.0,
        }

    def _normalize_dict(self, words: dict[str, str]) -> dict[str, str]:
        """Нормализует словарь слов.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.

        Returns:
            dict[str, str]: Новый словарь с нормализованными словами
            и переводами.

        Raises:
            ValueError: Если words не является словарём или если ключи
            или значения словаря не являются строками.
        """
        if not isinstance(words, dict):
            raise ValueError("words должен быть словарём")

        normalized_words: dict[str, str] = {}

        for word, translation in words.items():
            normalized_word = self.normalize_word(word)
            normalized_translation = self.normalize_word(translation)
            normalized_words[normalized_word] = normalized_translation

        return normalized_words

    @property
    def words(self) -> dict[str, str]:
        """Возвращает копию словаря слов.

        Returns:
            dict[str, str]: Копия словаря слов.
        """
        return copy.copy(self._words)

    @words.setter
    def words(self, words: dict[str, str]) -> None:
        """Заменяет словарь слов на новый с валидацией и нормализацией.

        Args:
            words: Новый словарь, где ключ — слово, а значение — перевод.

        Raises:
            ValueError: Если words не является словарём или если ключи
            или значения словаря не являются строками.
        """
        if self._session_active:
            raise ValueError(
                "Нельзя полностью заменить словарь во время "
                "активной тренировки"
            )
        self._words = self._normalize_dict(words)

    def start_session(self) -> None:
        """Начинает тренировочную сессию.

        Raises:
            ValueError: Если тренировочная сессия уже активна.
        """
        if self._session_active:
            raise ValueError("Тренировочная сессия уже активна")

        self._session_active = True
        self._session_start_time = time.time()
        self._session_user_score = 0
        self._last_word = None

    def end_session(self) -> None:
        """Завершает тренировочную сессию и сохраняет статистику.

        Raises:
            ValueError: Если тренировочная сессия не активна.
        """
        if not self._session_active:
            raise ValueError("Тренировочная сессия не активна")

        total_time = max(time.time() - self._session_start_time, 0.000001)

        self.last_session_stats = {
            "correct_answers": self._session_user_score,
            "total_time": total_time,
        }

        self._session_active = False
        self._session_start_time = 0.0
        self._last_word = None

    def get_random_word(self) -> str:
        """Возвращает случайное слово из словаря.

        Returns:
            Случайное слово из словаря.

        Raises:
            ValueError: Если словарь слов пуст.
        """
        if not self._words:
            raise ValueError("Нельзя выбрать слово из пустого словаря")

        random_word = random.choice(list(self._words.keys()))
        self._last_word = random_word
        return random_word

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

        if self._session_active:
            if self._last_word is None:
                raise ValueError(
                    "Нельзя проверить перевод без выданного слова"
                )

            if normalized_word != self._last_word:
                self.end_session()
                raise ValueError(
                    "Переданное слово не совпадает с последним выданным"
                )

        is_correct = self._words[normalized_word] == normalized_translation

        if self._session_active:
            if is_correct:
                self._session_user_score += 1
            self._last_word = None

        return is_correct

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

    def __iter__(self) -> Iterator[tuple[str, str]]:
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
