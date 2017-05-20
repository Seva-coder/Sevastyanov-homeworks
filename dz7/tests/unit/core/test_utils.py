import pytest

#import ipdb; ipdb.set_trace()
from create.utils import dev

class TestDev:
    def test_zero(self):
        result = dev(5, 0)
        assert result is None
