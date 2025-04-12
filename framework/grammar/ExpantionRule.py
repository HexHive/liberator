class ExpantionRule:
    def __init__(self, elements):
        self.new_elements = elements

    def __str__(self):
        return ";".join([str(e) for e in self.new_elements])

    def __iter__(self):
        for e in self.new_elements:
            yield e

    # for an element, the hash is just the key
    def __hash__(self):
        return hash(tuple(self.new_elements))
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)