class Genere:
    def __init__(self, genereID: int, name: str) -> None:
        self.genereID = genereID
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Genere) and self.genereID == other.genereID

    def __hash__(self):
        return hash(self.genereID)

    def __str__(self):
        return f"{self.name}"