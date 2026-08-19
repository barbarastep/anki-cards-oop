from pathlib import Path


class TextFileLoader:
    """Класс загрузки слов из текстового файла."""

    def __init__(self, *, file_path: str | Path
                 = "./words.txt") -> None:
        path = Path(file_path)

        if path.is_dir():
            raise ValueError(
                "file_path должен указывать на файл, "
                "а не на директорию"
            )

        self._file_path = path

    def load_words(self) -> dict[str, str]:
        """Загружает словарь слов из текстового файла."""
        words = {}

        if not self._file_path.exists():
            return {}

        with open(self._file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line.count(",") == 1:
                    word, translation = line.split(",", 1)
                    word = word.strip()
                    translation = translation.strip()
                    words[word] = translation

        return words

    def save_words(self, words: dict[str, str]) -> None:
        """Сохраняет словарь слов в текстовый файл."""
        if not isinstance(words, dict):
            raise ValueError("words должен быть словарём")

        file_path = self._file_path

        with open(file_path, "w", encoding="utf-8") as file:
            for word, translation in words.items():
                file.write(f"{word},{translation}\n")
