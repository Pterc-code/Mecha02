from pathlib import Path


class PraiseStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._praises: list[str] = []

    @property
    def praises(self) -> list[str]:
        return list(self._praises)

    async def load(self) -> list[str]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

        self._praises.clear()
        for line in self.path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                self._praises.append(stripped.split("||")[0])
        return self.praises

    async def add(self, praise: str, author: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        prefix = "\n" if self.path.exists() and self.path.stat().st_size > 0 else ""
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{prefix}{praise}||{author}")
        self._praises.append(praise)

    async def formatted_lines(self) -> list[str]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            return []
        return [
            line.strip().replace("||", ":  ")
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
