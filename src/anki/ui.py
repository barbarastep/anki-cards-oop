import textwrap

from anki.anki import Anki


class TextUI:
    """Класс приложения для текстового интерфейса."""

    STOP_WORD = "СТОП"

    MENU = textwrap.dedent("""\
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
        self._anki_game = anki_game

    def start_game(self) -> None:
        """Запускает режим тренировки перевода слов."""
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

    def add_words(self) -> None:
        """Запускает режим добавления новых слов."""
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
        """Выводит все пары слово-перевод."""
        words = self._anki_game.get_words()

        for word, translation in words.items():
            print(f"{word} - {translation}")

    def main_loop(self) -> None:
        """Запускает основной цикл меню пользовательского интерфейса."""
        while True:
            print(self.MENU)
            menu_item = input("\nПункт меню: ").strip()

            if menu_item == "1":
                self.start_game()
            elif menu_item == "2":
                self.add_words()
            elif menu_item == "3":
                print("Данная функциональность ещё не реализована")
            elif menu_item == "4":
                self.show_words()
            elif menu_item == "5":
                break
            else:
                print("Неизвестный пункт меню")
                print("Повторите ввод.")
