# expect: refuse array index must be an integer
# source: Regression corpus for a dict of lists stored as a class field
class Tables:
    lookup = {"warm": [1, 2, 3], "cool": [4, 5, 6]}

    def __init__(self):
        pass


tables = Tables()
print(tables.lookup["warm"][1])
