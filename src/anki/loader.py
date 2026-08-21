import json
import pathlib
from collections.abc import Callable
from typing import IO, Protocol, TypeVar


class WordsLoaderProtocol(Protocol):
    """Описывает общий интерфейс загрузчиков слов."""

    def load_words(self) -> dict[str, str]:
        """Загружает слова из источника.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
        """
        ...

    def save_words(self, words: dict[str, str]) -> None:
        """Сохраняет слова в источник.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.
        """
        ...


LoaderClass = TypeVar(
    "LoaderClass",
    bound=type[WordsLoaderProtocol],
)


class LoaderRegistry:
    """Хранит соответствие идентификаторов и классов загрузчиков."""

    def __init__(self) -> None:
        """Инициализирует пустой реестр загрузчиков."""
        self._registry: dict[str, type[WordsLoaderProtocol]] = {}

    def register(
        self,
        ident: str,
    ) -> Callable[[LoaderClass], LoaderClass]:
        """Регистрирует класс загрузчика по идентификатору.

        Args:
            ident: Идентификатор загрузчика.

        Returns:
            Декоратор, который сохраняет класс в реестре и возвращает его.
        """
        def decorator(loader_cls: LoaderClass) -> LoaderClass:
            self._registry[ident] = loader_cls
            return loader_cls

        return decorator

    def get_loader(self, ident: str) -> type[WordsLoaderProtocol]:
        """Возвращает класс загрузчика по идентификатору.

        Args:
            ident: Идентификатор загрузчика.

        Returns:
            Зарегистрированный класс загрузчика.

        Raises:
            ValueError: Если идентификатор не найден в реестре.
        """
        try:
            return self._registry[ident]
        except KeyError:
            raise ValueError(f"Неизвестный загрузчик: {ident}")


loader_registry = LoaderRegistry()


class BaseFileLoader:
    """Базовый класс для загрузчиков слов из файлов.

    Класс хранит путь к файлу и предоставляет общий интерфейс для загрузки
    и сохранения слов. Конкретный формат файла реализуется в наследниках.
    """

    def __init__(
        self,
        *,
        file_path: str | pathlib.Path = "./words.txt",
    ) -> None:
        """Инициализирует загрузчик файлового источника.

        Args:
            file_path: Путь к файлу со словами.

        Raises:
            ValueError: Если переданный путь указывает на директорию.
        """
        self._file_path: pathlib.Path = pathlib.Path(file_path)

        if self._file_path.exists() and self._file_path.is_dir():
            raise ValueError(
                f"Путь {file_path} является директорией, а должен быть файлом"
            )

    def load_words(self) -> dict[str, str]:
        """Загружает слова из файла.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
            Если файл не существует, возвращает пустой словарь.
        """
        if not self._file_path.exists():
            return {}

        with self._file_path.open("r", encoding="utf-8") as f:
            return self._load_from_file(f)

    def save_words(self, words: dict[str, str]) -> None:
        """Сохраняет слова в файл.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.

        Raises:
            ValueError: Если words не является словарём.
        """
        if not isinstance(words, dict):
            raise ValueError("Значением параметра `words` должен быть словарь")

        with self._file_path.open("w", encoding="utf-8") as f:
            return self._save_to_file(words, f)

    def _load_from_file(self, file_object: IO[str]) -> dict[str, str]:
        """Загружает слова из открытого файлового объекта.

        Метод должен быть переопределён в наследниках для конкретного
        формата файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.

        Raises:
            NotImplementedError: Если метод не переопределён в наследнике.
        """
        raise NotImplementedError

    def _save_to_file(
        self,
        words: dict[str, str],
        file_object: IO[str],
    ) -> None:
        """Сохраняет слова в открытый файловый объект.

        Метод должен быть переопределён в наследниках для конкретного
        формата файла.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.
            file_object: Открытый файловый объект для записи.

        Raises:
            NotImplementedError: Если метод не переопределён в наследнике.
        """
        raise NotImplementedError


@loader_registry.register(".txt")
class TextFileLoader(BaseFileLoader):
    """Загрузчик слов из текстового файла с разделителем-запятой.

    Поддерживает формат строки: ``слово,перевод``.
    """

    DEFAULT_FILE_PATH: str = "./words.txt"

    def _load_from_file(self, file_object: IO[str]) -> dict[str, str]:
        """Загружает слова из CSV-подобного текстового файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
        """

        words: dict[str, str] = {}
        for line in file_object:
            word, translation = line.split(",")
            words[word.strip()] = translation.strip()
        return words

    def _save_to_file(
        self,
        words: dict[str, str],
        file_object: IO[str],
    ) -> None:
        """Сохраняет слова в CSV-подобный текстовый файл.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.
            file_object: Открытый файловый объект для записи.
        """
        for word, translation in words.items():
            file_object.write(f'{word},{translation}\n')


@loader_registry.register(".tsv")
class TSVFileLoader(BaseFileLoader):
    """Загрузчик слов из TSV-файла.

    Поддерживает формат строки: ``слово\tперевод``.
    """

    DEFAULT_FILE_PATH: str = "./words.tsv"

    def _load_from_file(self, file_object: IO[str]) -> dict[str, str]:
        """Загружает слова из TSV-файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
        """
        words: dict[str, str] = {}
        for line in file_object:
            word, translation = line.split("\t")
            words[word.strip()] = translation.strip()
        return words

    def _save_to_file(
        self,
        words: dict[str, str],
        file_object: IO[str],
    ) -> None:
        """Сохраняет слова в TSV-файл.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.
            file_object: Открытый файловый объект для записи.
        """
        for word, translation in words.items():
            file_object.write(f'{word}\t{translation}\n')


@loader_registry.register(".json")
class JsonFileLoader(BaseFileLoader):
    """Загрузчик слов из JSON-файла.

    Работает с JSON-файлом, где данные хранятся в формате:
    {"слово": "перевод"}.
    """

    DEFAULT_FILE_PATH: str = "./words.json"

    def _load_from_file(self, file_object: IO[str]) -> dict[str, str]:
        """Загружает слова из JSON-файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            dict[str, str]: Словарь со словами и переводами.
        """

        words: dict[str, str] = json.load(file_object)

        for word, translation in words.items():
            if not isinstance(word, str) or not isinstance(translation, str):
                raise ValueError("Некорректные данные в JSON-файле")

        return words

    def _save_to_file(
        self,
        words: dict[str, str],
        file_object: IO[str],
    ) -> None:
        """Сохраняет слова в JSON-файл.

        Args:
            words: Словарь со словами и переводами.
            file_object: Открытый файловый объект для записи.
        """

        json.dump(words, file_object, indent=2, ensure_ascii=False)


@loader_registry.register("http")
class JsonNetworkLoader:
    """Загрузчик слов из JSON-файла по URL.

    Работает с JSON-файлом, где данные хранятся в формате:
    {"слово": "перевод"}.
    """

    def __init__(self, url: str) -> None:
        """Инициализирует загрузчик сетевого JSON-источника.

        Args:
            url: URL-адрес JSON-файла со словами.
        """
        self.url: str = url

    def load_words(self) -> dict[str, str]:
        """Загружает слова из JSON-файла по URL.

        Returns:
            dict[str, str]: Словарь со словами и переводами.
        """
        import requests

        response = requests.get(self.url)
        response.raise_for_status()

        words: dict[str, str] = response.json()

        for word, translation in words.items():
            if not isinstance(word, str) or not isinstance(translation, str):
                raise ValueError("Некорректные данные получены по сети")

        return words

    def save_words(self, words: dict[str, str]) -> None:
        """Оставляет сетевой источник без изменений.

        Args:
            words: Словарь слов, который не сохраняется для сетевого источника.
        """
        pass
