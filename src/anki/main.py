import argparse
from collections.abc import Generator
from contextlib import contextmanager

from anki.anki import Anki
from anki.loader import LoaderProtocol, loader_registry
from anki.ui import TextUI


def get_loader(source: str) -> LoaderProtocol:
    """Возвращает загрузчик для переданного источника слов.

    Args:
        source: Путь к файлу или URL.

    Returns:
        Экземпляр подходящего загрузчика.
    """
    loader_cls = loader_registry.get_loader(source)
    return loader_cls.from_source(source)


@contextmanager
def game_context(
    loader: LoaderProtocol,
    anki: Anki,
) -> Generator[Anki, None, None]:
    """Управляет загрузкой и сохранением слов для игровой сессии.

    При входе в контекст загружает слова через загрузчик и записывает их
    в экземпляр игры. При выходе сохраняет актуальные слова через загрузчик.

    Args:
        loader: Загрузчик слов с методами load_words() и save_words().
        anki: Экземпляр игры, в который загружаются слова.

    Yields:
        Экземпляр игры с загруженными словами.
    """
    anki.words = loader.load_words()

    try:
        yield anki
    finally:
        loader.save_words(anki.words)


def main() -> None:
    """Запускает консольное приложение Anki."""
    parser = argparse.ArgumentParser(prog="anki")

    parser.add_argument(
        "--source", default="./words.txt",
        help="Путь или ссылка до источника со словами",
        metavar="SOURCE",
    )

    args = parser.parse_args()

    loader = get_loader(args.source)

    anki = Anki()

    with game_context(loader, anki) as game:
        ui = TextUI(game)
        ui.main_loop()


if __name__ == "__main__":
    main()
