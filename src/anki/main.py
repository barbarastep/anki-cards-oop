import argparse
import pathlib
from contextlib import contextmanager

from anki.anki import Anki
from anki.loader import (
    JsonFileLoader,
    JsonNetworkLoader,
    TextFileLoader,
    TSVFileLoader,
)
from anki.ui import TextUI


def get_loader(source):
    """Выбирает реализацию загрузчика в зависимости от `source`.

    Parameters
    ----------
    source : str
        Источник для получения слов, файл.

    Returns
    -------
    Any
        Класс загрузчика
    """

    loaders = {
        ".txt": TextFileLoader,
        ".tsv": TSVFileLoader,
        ".json": JsonFileLoader
    }

    if source.startswith("http") or source.startswith("https"):
        return JsonNetworkLoader(source)

    file_path = pathlib.Path(source)

    try:
        # suffix возвращает расширение файла
        loader = loaders[file_path.suffix]
        return loader(file_path=str(file_path))
    except KeyError:
        raise ValueError(f"Неизвестный тип источника слов: {source}")


@contextmanager
def game_context(loader, anki):
    """Управляет жизненным циклом игры.

    Args:
        loader: Экземпляр загрузчика слов.
        anki: Экземпляр игры Anki.

    Yields:
        Anki: Экземпляр игры с загруженными словами.
    """
    anki.words = loader.load_words()

    try:
        yield anki
    finally:
        loader.save_words(anki.words)


def main():
    # Создали объект парсера аргументов командной строки.
    parser = argparse.ArgumentParser(prog="anki")

    # Добавили новый аргумент.
    parser.add_argument(
        "--source", default="./words.txt",
        help="Путь или ссылка до источника со словами",
        metavar="SOURCE",
    )

    # Распарсили аргументы командной строки.
    args = parser.parse_args()

    loader = get_loader(args.source)

    anki = Anki()

    with game_context(loader, anki) as game:
        ui = TextUI(game)
        ui.main_loop()


if __name__ == "__main__":
    main()
