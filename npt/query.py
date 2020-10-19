import npt

class Query(object):
    """
    Interface for provider specific queries

    Attributes:
        _result: stores data model/structure from query results (default: None)
    """
    _result = None

    def __init__(self, *args, **kwargs):
        super().__init__()

    @property
    def result(self):
        return self._result

    def search(self):
        return self

    @property
    def products(self):
        NotImplementedError("This is a base query object, you should not be here.")
