import copy
import random
import time
from collections.abc import Iterator


class TrainingSession:
    """Хранит состояние одной тренировочной сессии."""

    def __init__(self, anki: "Anki") -> None:
        """Инициализирует тренировочную сессию.

        Args:
            anki: Экземпляр Anki, из которого берутся слова и переводы.
        """
        self.active: bool = True
        self._anki: Anki = anki
        self._start_time: float = time.time()
        self._end_time: float = self._start_time
        self._user_score: int = 0
        self._last_word: str | None = None

    def get_random_word(self) -> str:
        """Возвращает случайное слово и запоминает его в сессии.

        Returns:
            Случайное слово из словаря Anki.

        Raises:
            ValueError: Если сессия не активна.
        """
        if not self.active:
            raise ValueError("Тренировочная сессия не активна")
        word = self._anki.get_random_word()
        self._last_word = word
        return word

    def check_translation(self, word: str, translation: str) -> bool:
        """Проверяет перевод слова в рамках текущей сессии.

                Args:
                    word: Слово для проверки.
                    translation: Перевод пользователя.

                Returns:
                    True, если перевод верный, иначе False.

                Raises:
                    ValueError: Если сессия не активна, если проверяется
                        не последнее выданное слово или если слово ещё
                            не выдавалось.
        """
        if not self.active:
            raise ValueError("Тренировочная сессия не активна")
        normalized_word = self._anki.normalize_word(word)

        if self._last_word is None:
            raise ValueError("Нельзя проверить перевод без выданного слова")

        if normalized_word != self._last_word:
            self.end_session()
            raise ValueError(
                "Переданное слово не совпадает с последним выданным"
            )

        is_correct = self._anki.check_translation(word, translation)

        self._last_word = None
        return is_correct

    def end_session(self) -> None:
        """Завершает тренировочную сессию.

        Raises:
            ValueError: Если сессия уже не активна.
        """
        if not self.active:
            raise ValueError("Тренировочная сессия не активна")

        self.active = False
        self._end_time = time.time()
        self._anki.end_session()

    def get_stat(self) -> dict[str, int | float]:
        """Возвращает статистику тренировочной сессии.

        Returns:
            Словарь с количеством правильных ответов и временем тренировки.
        """
        if self.active:
            total_time = time.time() - self._start_time
        else:
            total_time = self._end_time - self._start_time

        return {
            "correct_answers": self._user_score,
            "total_time": total_time,
        }


class ZeroMistakesTraining(TrainingSession):
    """Тренировка до первой ошибки."""

    def check_translation(self, word: str, translation: str) -> bool:
        """Проверяет перевод и завершает тренировку при первой ошибке.

        Args:
            word: Слово для проверки.
            translation: Перевод пользователя.

        Returns:
            True, если перевод верный, иначе False.
        """
        is_correct = super().check_translation(word, translation)

        if is_correct:
            self._user_score += 1
        else:
            self.end_session()

        return is_correct


class TimeLimitedTraining(TrainingSession):
    """Тренировка с ограничением по времени."""

    def __init__(
        self,
        anki: "Anki",
        time_limit: float = 60.0,
    ) -> None:
        """Инициализирует тренировку с ограничением по времени.

        Args:
            anki: Экземпляр Anki, из которого берутся слова и переводы.
            time_limit: Лимит времени тренировки в секундах.
        """
        super().__init__(anki)
        self._time_limit: float = time_limit

    def check_translation(self, word: str, translation: str) -> bool:
        """Проверяет перевод и завершает сессию, если время истекло.

        Args:
            word: Слово для проверки.
            translation: Перевод пользователя.

        Returns:
            True, если перевод верный, иначе False.
        """

        is_correct = super().check_translation(word, translation)

        if is_correct:
            self._user_score += 1

        if time.time() - self._start_time >= self._time_limit:
            self.end_session()

        return is_correct


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

    def start_zero_mistakes_training(self) -> TrainingSession:
        """Начинает тренировку до первой ошибки.

        Returns:
            Объект тренировочной сессии.

        Raises:
            RuntimeError: Если тренировка уже активна.
        """
        if self._session_active:
            raise RuntimeError("Нельзя начать тренировку, если она уже начата")

        self._session_active = True
        return ZeroMistakesTraining(self)

    def start_time_limited_training(
        self,
        time_limit: float = 60.0,
    ) -> TrainingSession:
        """Начинает тренировку с ограничением по времени.

        Args:
            time_limit: Лимит времени тренировки в секундах.

        Returns:
            Объект тренировки с ограничением по времени.

        Raises:
            RuntimeError: Если тренировка уже активна.
        """
        if self._session_active:
            raise RuntimeError("Нельзя начать тренировку, если она уже начата")

        self._session_active = True
        return TimeLimitedTraining(self, time_limit)

    def end_session(self) -> None:
        """Завершает активную тренировочную сессию.

        Raises:
            RuntimeError: Если активной тренировки нет.
        """
        if not self._session_active:
            raise RuntimeError("Нельзя завершить неактивную сессию тренировки")

        self._session_active = False

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

        is_correct = self._words[normalized_word] == normalized_translation

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
