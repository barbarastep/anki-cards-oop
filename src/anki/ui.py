from collections.abc import Callable

from anki.anki import Anki


class TextUI:
    """Отвечает за консольный интерфейс.

    Класс выводит меню, принимает пользовательский ввод и вызывает методы
    объекта Anki для выполнения игровых действий.
    """

    STOP_WORD: str = "СТОП"

    def __init__(self, anki_game: Anki) -> None:
        """Инициализирует текстовый интерфейс.

        Args:
            anki_game: Экземпляр класса Anki для работы с игрой.
        """
        self._is_running: bool = False
        self._anki_game: Anki = anki_game
        self._command_definition: list[
            tuple[Callable[[], None], str, Callable[[], bool]]
        ] = [
            (
                self.start_game,
                "Начать игру",
                lambda: len(self._anki_game) > 0,
            ),
            (
                self.add_words,
                "Добавить слова",
                lambda: True,
            ),
            (
                self.train_until_mistake,
                "Тренировка до первой ошибки",
                lambda: len(self._anki_game) > 0,
            ),
            (
                self.train_until_time_runs_out,
                "Тренировка на время",
                lambda: len(self._anki_game) > 0,
            ),
            (
                self.show_words,
                "Показать все слова",
                lambda: len(self._anki_game) > 0,
            ),
            (
                self.find_translation,
                "Найти перевод",
                lambda: len(self._anki_game) > 0,
            ),
            (
                self.stop,
                "Выход",
                lambda: True,
            ),
        ]

    def stop(self) -> None:
        """Останавливает основной цикл меню."""
        self._is_running = False

    def get_available_commands(
        self,
    ) -> list[tuple[Callable[[], None], str]]:
        """Возвращает команды, доступные в текущем состоянии игры.

        Returns:
            Список пар: функция команды и её описание.
        """
        commands: list[tuple[Callable[[], None], str]] = []

        for func, description, is_visible in self._command_definition:
            if is_visible():
                commands.append((func, description))

        return commands

    def start_game(self) -> None:
        """Запускает обычный режим тренировки.

        Пользователь переводит случайные слова до ввода стоп-слова.
        """
        print(f"Чтобы закончить, введите {self.STOP_WORD}")

        while True:
            word = self._anki_game.get_random_word()
            print(f"Ваше слово: {word}")

            translation = input("Ваш перевод: ")

            if translation.strip().upper() == self.STOP_WORD:
                break

            if self._anki_game.check_translation(word, translation):
                print("Верно!")
            else:
                correct_translation = self._anki_game.get_translation(word)
                print(
                    "Неправильно, правильный ответ: " f"{correct_translation}"
                )

    def train_until_mistake(self) -> None:
        """Запускает тренировку до первой ошибки.

        Начинает тренировочную сессию в объекте Anki, задаёт случайные слова
        и завершает режим после первого неверного ответа или стоп-слова.
        """
        print(
            "Удачной игры до первой ошибки! "
            f"Чтобы завершить игру введите: {self.STOP_WORD}"
        )

        training_session = self._anki_game.start_zero_mistakes_training()

        while True:
            word = training_session.get_random_word()
            print(f"Переведите слово: {word}")

            translation = input()

            if translation == self.STOP_WORD:
                training_session.end_session()
                user_stat = training_session.get_stat()
                print(
                    f"Итоговый счёт: {user_stat['correct_answers']}, "
                    f"время игры: {user_stat['total_time']:.3f} секунд"
                )
                break

            is_correct = training_session.check_translation(word, translation)

            if is_correct:
                print("Все верно!")
            else:
                user_stat = training_session.get_stat()
                print(
                    "Неправильно, игра окончена, ваш вариант "
                    f"{translation!r} правильный перевод: "
                    f"{self._anki_game.get_translation(word)}"
                )
                print(
                    f"Итоговый счёт: {user_stat['correct_answers']}, "
                    f"время игры: {user_stat['total_time']:.3f} секунд"
                )
                break

    def train_until_time_runs_out(self) -> None:
        """Запускает тренировку с ограничением по времени."""
        print(
            "Удачной игры на время! "
            f"Чтобы завершить игру введите: {self.STOP_WORD}"
        )

        time_limit = float(input("Введите время игры в секундах: "))
        training_session = self._anki_game.start_time_limited_training(
            time_limit
        )

        while training_session.active:
            word = training_session.get_random_word()
            print(f"Переведите слово: {word}")

            translation = input()

            if translation == self.STOP_WORD:
                training_session.end_session()
                break

            is_correct = training_session.check_translation(word, translation)

            if is_correct:
                print("Все верно!")
            else:
                print(
                    "Неправильно, правильный ответ: "
                    f"{self._anki_game.get_translation(word)}"
                )

        user_stat = training_session.get_stat()
        print(
            f"Итоговый счёт: {user_stat['correct_answers']}, "
            f"время игры: {user_stat['total_time']:.3f} секунд"
        )

    def add_words(self) -> None:
        """Запускает режим добавления новых слов.

        Запрашивает у пользователя пары слово-перевод и добавляет их
        в объект Anki до ввода стоп-слова.
        """
        print(f"Чтобы закончить, введите {self.STOP_WORD}")

        while True:
            word = input("Введите слово: ").strip()
            if word.upper() == self.STOP_WORD:
                break

            translation = input("Введите перевод: ").strip()
            if translation.upper() == self.STOP_WORD:
                break

            self._anki_game.add_word(word, translation)

    def show_words(self) -> None:
        """Выводит количество слов и все пары слово-перевод.

        Использует итерацию по объекту Anki и стандартную функцию len().
        """
        print(f"Всего слов: {len(self._anki_game)}")

        for word, translation in self._anki_game:
            print(f"{word} - {translation}")

    def find_translation(self) -> None:
        """Ищет и выводит перевод слова из словаря игры."""
        word = input("Введите слово для поиска: ").strip()

        if word in self._anki_game:
            translation = self._anki_game.get_translation(word)
            print(f"{word} - {translation}")
        else:
            print("Слово не найдено")

    def main_loop(self) -> None:
        """Запускает основной цикл меню с доступными командами."""
        self._is_running = True

        while self._is_running:
            menu_choices: list[str] = []
            commands: dict[str, Callable[[], None]] = {}

            for index, command in enumerate(
                self.get_available_commands(),
                start=1,
            ):
                func, description = command
                menu_choices.append(f"{index}. {description}")
                commands[str(index)] = func

            print("Меню:\n" + "\n".join(menu_choices))
            menu_item = input("Пункт меню: ").strip()

            if menu_item in commands:
                commands[menu_item]()
            else:
                print("Неизвестный пункт меню")
                print("Повторите ввод.")

            print()
