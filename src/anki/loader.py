import json
import pathlib
from collections.abc import Callable
from typing import IO, Protocol, Self, cast


class LoaderProtocol(Protocol):
    """Описывает общий интерфейс загрузчиков слов."""

    @classmethod
    def from_source(cls, source: str) -> Self:
        """Создаёт загрузчик из строки-источника.

        Args:
            source: Путь к файлу или URL.

        Returns:
            Экземпляр загрузчика.
        """
        ...

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


class LoaderRegistry:
    """Хранит классы загрузчиков и условия их выбора."""

    def __init__(self) -> None:
        """Инициализирует пустой реестр загрузчиков."""
        self._registry: dict[
            str | type[LoaderProtocol],
            type[LoaderProtocol] | Callable[[str], bool],
        ] = {}

    def register(
        self,
        predicate: Callable[[str], bool],
    ) -> Callable[[type[LoaderProtocol]], type[LoaderProtocol]]:
        """Регистрирует класс загрузчика с условием выбора.

        Args:
            predicate: Функция, которая проверяет, подходит ли загрузчик
                для переданного источника.

        Returns:
            Декоратор, который сохраняет класс загрузчика в реестре.
        """

        def decorator(
            loader_cls: type[LoaderProtocol],
        ) -> type[LoaderProtocol]:
            if isinstance(predicate, str):
                self._registry[predicate] = loader_cls
            else:
                self._registry[loader_cls] = predicate

            return loader_cls

        return decorator

    def get_loader(self, source: str) -> type[LoaderProtocol]:
        """Находит подходящий класс загрузчика для источника.

        Args:
            source: Путь к файлу или URL.

        Returns:
            Класс загрузчика, подходящий для source.

        Raises:
            ValueError: Если подходящий загрузчик не найден.
        """
        for key, value in self._registry.items():
            if isinstance(key, str) and key == source:
                if isinstance(value, type):
                    return value

            if not isinstance(key, str):
                predicate = cast(Callable[[str], bool], value)
                if predicate(source):
                    return key

        raise ValueError(f"Неизвестный источник: {source}")


loader_registry = LoaderRegistry()


@loader_registry.register(lambda source: source.startswith("http"))
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

    @classmethod
    def from_source(cls, source: str) -> Self:
        """Создаёт сетевой загрузчик из URL.

        Args:
            source: URL-адрес JSON-файла со словами.

        Returns:
            Экземпляр сетевого загрузчика.
        """
        return cls(source)

    def load_words(self) -> dict[str, str]:
        """Загружает слова из JSON-файла по URL.

        Returns:
            dict[str, str]: Словарь со словами и переводами.
        """
        import requests

        response = requests.get(self.url)
        response.raise_for_status()

        words: dict[str, str] = response.json()

        if not isinstance(words, dict):
            raise ValueError("Некорректные данные получены по сети")

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

    @classmethod
    def from_source(cls, source: str) -> Self:
        """Создаёт файловый загрузчик из пути к файлу.

        Args:
            source: Путь к файлу со словами.

        Returns:
            Экземпляр файлового загрузчика.
        """
        return cls(file_path=source)

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


@loader_registry.register(lambda source: source.endswith(".txt"))
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
            file_object.write(f"{word},{translation}\n")


@loader_registry.register(lambda source: source.endswith(".tsv"))
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
            file_object.write(f"{word}\t{translation}\n")


@loader_registry.register(lambda source: source.endswith(".json"))
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

        if not isinstance(words, dict):
            raise ValueError("Некорректные данные в JSON-файле")

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
