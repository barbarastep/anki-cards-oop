import json
import pathlib


class BaseFileLoader:
    """Базовый класс для загрузчиков слов из файлов.

    Класс хранит путь к файлу и предоставляет общий интерфейс для загрузки
    и сохранения слов. Конкретный формат файла реализуется в наследниках.
    """

    def __init__(self, *, file_path='./words.txt'):
        self._file_path = pathlib.Path(file_path)

        if self._file_path.exists() and self._file_path.is_dir():
            raise ValueError(
                f"Путь {file_path} является директорией, а должен быть файлом"
            )

    def load_words(self):
        """Загружает слова из файла.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
            Если файл не существует, возвращает пустой словарь.
        """
        if not self._file_path.exists():
            return {}

        with self._file_path.open("r", encoding="utf-8") as f:
            return self._load_from_file(f)

    def save_words(self, words):
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

    def _load_from_file(self, file_object):
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

    def _save_to_file(self, words, file_object):
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


class TextFileLoader(BaseFileLoader):
    """Загрузчик слов из текстового файла с разделителем-запятой.

    Поддерживает формат строки: ``слово,перевод``.
    """

    DEFAULT_FILE_PATH = "./words.txt"

    def _load_from_file(self, file_object):
        """Загружает слова из CSV-подобного текстового файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
        """

        words = {}
        for line in file_object:
            word, translation = line.split(",")
            words[word.strip()] = translation.strip()
        return words

    def _save_to_file(self, words, file_object):
        """Сохраняет слова в CSV-подобный текстовый файл.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.
            file_object: Открытый файловый объект для записи.
        """
        for word, translation in words.items():
            file_object.write(f'{word},{translation}\n')


class TSVFileLoader(BaseFileLoader):
    """Загрузчик слов из TSV-файла.

    Поддерживает формат строки: ``слово\tперевод``.
    """

    DEFAULT_FILE_PATH = "./words.tsv"

    def _load_from_file(self, file_object):
        """Загружает слова из TSV-файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            Словарь, где ключ — слово, а значение — перевод.
        """
        words = {}
        for line in file_object:
            word, translation = line.split("\t")
            words[word.strip()] = translation.strip()
        return words

    def _save_to_file(self, words, file_object):
        """Сохраняет слова в TSV-файл.

        Args:
            words: Словарь, где ключ — слово, а значение — перевод.
            file_object: Открытый файловый объект для записи.
        """
        for word, translation in words.items():
            file_object.write(f'{word}\t{translation}\n')


class JsonFileLoader(BaseFileLoader):
    """Загрузчик слов из JSON-файла.

    Работает с JSON-файлом, где данные хранятся в формате:
    {"слово": "перевод"}.
    """

    DEFAULT_FILE_PATH = "./words.json"

    def _load_from_file(self, file_object) -> dict[str, str]:
        """Загружает слова из JSON-файла.

        Args:
            file_object: Открытый файловый объект для чтения.

        Returns:
            dict[str, str]: Словарь со словами и переводами.
        """

        return json.load(file_object)

    def _save_to_file(self, words: dict[str, str], file_object) -> None:
        """Сохраняет слова в JSON-файл.

        Args:
            words: Словарь со словами и переводами.
            file_object: Открытый файловый объект для записи.
        """

        json.dump(words, file_object, indent=2, ensure_ascii=False)
