import textwrap

from anki.anki import Anki


class TextUI:
    """Отвечает за консольный интерфейс.

    Класс выводит меню, принимает пользовательский ввод и вызывает методы
    объекта Anki для выполнения игровых действий.
    """

    STOP_WORD: str = "СТОП"

    MENU: str = textwrap.dedent("""\
        Меню:
        1. Начать игру
        2. Добавить слова
        3. Тренировка до первой ошибки
        4. Вывод всех слов
        5. Выход
    """)

    def __init__(self, anki_game: Anki) -> None:
        """Инициализирует текстовый интерфейс.

        Args:
            anki_game: Экземпляр класса Anki для работы с игрой.
        """
        self._anki_game: Anki = anki_game

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
                    "Неправильно, правильный ответ: "
                    f"{correct_translation}"
                )

    def train_until_mistake(self) -> None:
        """Запускает тренировку до первой ошибки.

        Начинает тренировочную сессию в объекте Anki, задаёт случайные слова
        и завершает режим после первого неверного ответа или стоп-слова.
        """
        print(f"Чтобы закончить, введите {self.STOP_WORD}")

        self._anki_game.start_session()

        while True:
            word = self._anki_game.get_random_word()
            print(f"Ваше слово: {word}")

            translation = input("Ваш перевод: ")

            if translation.strip().upper() == self.STOP_WORD:
                break

            is_correct = self._anki_game.check_translation(word, translation)

            if is_correct:
                print("Верно!")
            else:
                correct_translation = self._anki_game.get_translation(word)
                print(
                    "Неправильно, правильный ответ: "
                    f"{correct_translation}"
                )
                break

        self._anki_game.end_session()

        print(
            "Правильных ответов: "
            f"{self._anki_game.last_session_stats['correct_answers']}"
        )
        print(
            "Время тренировки: "
            f"{self._anki_game.last_session_stats['total_time']:.2f}"
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

    def main_loop(self) -> None:
        """Запускает основной цикл меню.

        Показывает пункты меню, обрабатывает пользовательский выбор
        и вызывает соответствующие методы интерфейса.
        """
        while True:
            print(self.MENU)
            menu_item = input("\nПункт меню: ").strip()

            if menu_item == "1":
                self.start_game()
            elif menu_item == "2":
                self.add_words()
            elif menu_item == "3":
                self.train_until_mistake()
            elif menu_item == "4":
                self.show_words()
            elif menu_item == "5":
                break
            else:
                print("Неизвестный пункт меню")
                print("Повторите ввод.")
