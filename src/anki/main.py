import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


STOP_WORD = 'СТОП'


def is_stop(value: str) -> bool:
    """Проверяет, ввёл ли пользователь служебное слово для остановки."""
    return value.strip().upper() == STOP_WORD


def load_words(filename: str = "words.txt") -> Dict[str, str]:
    """Загружает словарь слов из текстового файла."""
    words = {}

    file_path = Path(filename)
    if not file_path.exists():
        file_path = Path(__file__).with_name(filename)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line.count(",") == 1:
                    word, translation = line.split(",", 1)
                    word = word.strip()
                    translation = translation.strip()
                    words[word] = translation
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден.")
        sys.exit(1)

    return words


def save_words(
    words: Dict[str, str],
    filename: str = "words.txt",
) -> None:
    """Сохраняет словарь слов в текстовый файл."""
    file_path = Path(filename)
    if not file_path.exists():
        file_path = Path(__file__).with_name(filename)

    with open(file_path, "w", encoding="utf-8") as file:
        for word, translation in words.items():
            file.write(f"{word}, {translation}\n")

    print(f"Было сохранено {len(words)} слов в файл {filename}")


def show_menu() -> None:
    """Выводит главное меню программы."""
    print("\nМеню:")
    print("1. Начать игру")
    print("2. Добавить слова")
    print("3. Тренировка до первой ошибки")
    print("4. Вывод всех слов")
    print("5. Выход")


def get_random_words(words: Dict[str, str]) -> List[Tuple[str, str]]:
    """Возвращает перемешанный список пар слово-перевод."""
    word_items = list(words.items())
    random.shuffle(word_items)
    return word_items


def print_statistics(score: int, total_time: float) -> None:
    """Выводит итоговую статистику игровой сессии."""
    print(f"Ваш итоговый счет: {score}")

    if score > 0:
        average_time = f"{total_time / score:.2f} сек."
    else:
        average_time = "—"

    print(
        f"Время игры: {total_time:.2f} секунд "
        f"(среднее время: {average_time})"
    )


def ask_and_check(word: str, correct: str) -> Tuple[bool, bool, float]:
    """Запрашивает перевод слова и возвращает результат проверки."""
    print(f"Ваше слово: {word}")

    start_time = time.time()
    answer = input("Ваш перевод: ")
    end_time = time.time()

    if is_stop(answer):
        return True, False, 0.0

    answer_time = end_time - start_time
    is_correct = answer.strip().lower() == correct.strip().lower()

    return False, is_correct, answer_time


def start_game(words: Dict[str, str]) -> None:
    """Запускает обычный игровой режим тренировки слов."""
    if not words:
        print("Словарь пуст. Сначала добавьте слова.")
        return

    print("Чтобы закончить, введите СТОП")
    score = 0
    total_answer_time = 0

    word_items = list(words.items())

    while True:
        word, translation = random.choice(word_items)
        should_exit, is_correct, answer_time = ask_and_check(
            word,
            translation,
        )

        if should_exit:
            break

        total_answer_time += answer_time

        if is_correct:
            score += 1
            print(f"Верно! Время на ответ: {answer_time:.2f} секунд")
        else:
            print(
                f"Неправильно, правильный ответ: {translation} "
                f"(Время на ответ: {answer_time:.2f} секунд)"
            )

    print("Спасибо за игру!")
    print_statistics(score, total_answer_time)


def add_words(words: Dict[str, str]) -> None:
    """Добавляет новые пары слово-перевод в словарь."""
    print("Чтобы закончить, введите СТОП")

    while True:
        word = input("Введите слово: ").strip()
        if is_stop(word):
            break
        if not word:
            print("Слово не может быть пустым. Повторите ввод.")
            continue

        translation = input("Введите перевод: ").strip()
        if is_stop(translation):
            break
        if not translation:
            print("Перевод не может быть пустым. Повторите ввод.")
            continue

        words[word] = translation


def train_until_mistake(words: Dict[str, str]) -> None:
    """Запускает тренировку до первой ошибки."""
    if not words:
        print("Словарь пуст. Сначала добавьте слова.")
        return

    print(
        "\nРежим: Игра до первой ошибки! "
        "Чтобы выйти вручную, введите СТОП\n"
    )
    score = 0
    total_answer_time = 0

    for word, translation in get_random_words(words):
        should_exit, is_correct, answer_time = ask_and_check(
            word,
            translation,
        )

        if should_exit:
            print("Выход из режима по запросу пользователя.")
            break

        total_answer_time += answer_time

        if is_correct:
            score += 1
            print(
                f"Верно! Всего очков: {score} "
                f"(ответ за {answer_time:.2f} секунд)"
            )
        else:
            print(f"Ошибка! Неверно. Правильный ответ: {translation}")
            break

    print_statistics(score, total_answer_time)


def show_all_words(words: Dict[str, str]) -> None:
    """Выводит все пары слово-перевод одной строкой."""
    all_words = []

    for word, translation in words.items():
        all_words.append(f"{word} - {translation}")

    print("; ".join(all_words))


def main() -> None:
    """Запускает основной цикл меню приложения."""
    filename = "words.txt"
    words = load_words()
    print(f"Было загружено {len(words)} слов из файла {filename}")

    while True:
        show_menu()
        menu_item = input("\nПункт меню: ").strip()

        if menu_item == "1":
            start_game(words)
        elif menu_item == "2":
            add_words(words)
        elif menu_item == "3":
            train_until_mistake(words)
        elif menu_item == "4":
            show_all_words(words)
        elif menu_item == "5":
            save_words(words)
            sys.exit()
        else:
            print("Неизвестный пункт меню")
            print("Повторите ввод.")


if __name__ == "__main__":
    main()
