"Test sortedcollections.recipes"

import pickle

import pytest

from sortedcollections import IndexableDict, IndexableSet, SegmentList


def test_index_dict():
    mapping = IndexableDict(enumerate(range(10)))
    iloc = mapping.keys()
    for value in range(10):
        assert iloc[value] == value


def test_index_set():
    set_values = IndexableSet(range(10))
    for index in range(10):
        assert set_values[index] == index


def test_index_set_pickle():
    set_values1 = IndexableSet(range(10))
    data = pickle.dumps(set_values1)
    set_values2 = pickle.loads(data)
    assert set_values1 == set_values2


def test_segment_list():
    values = [5, 1, 3, 2, 4, 8, 6, 7, 9, 0]
    sl = SegmentList(values)
    assert list(sl) == values
    sl.sort()
    assert list(sl) == list(range(10))
    sl.reverse()
    assert list(sl) == list(reversed(range(10)))
    sl.reverse()
    sl.append(10)
    assert list(sl) == list(range(11))
    sl.extend(range(11, 15))
    assert list(sl) == list(range(15))
    del sl[5:]
    assert list(sl) == list(range(5))
    sl[2] = 'c'
    sl.insert(3, 'd')
    sl.insert(6, 'e')
    assert list(sl) == [0, 1, 'c', 'd', 3, 4, 'e']


def test_segment_list_bisect():
    sl = SegmentList()
    with pytest.raises(NotImplementedError):
        sl.bisect(0)


def test_segment_list_setitem_slice():
    sl = SegmentList()
    with pytest.raises(NotImplementedError):
        sl[:] = [0]


@pytest.mark.parametrize('size', [0, 1, 7, 2100])
def test_segment_list_extend_self(size):
    values = list(range(size))
    mapping = SegmentList(values)
    append = mapping.append

    def bounded_append(value):
        # Make a regression fail rather than growing the list indefinitely.
        assert len(mapping) < 2 * size
        append(value)

    mapping.append = bounded_append
    result = mapping.extend(mapping)
    assert result is None
    assert list(mapping) == values + values
    mapping._check()


@pytest.mark.parametrize('size', [0, 1, 7, 2100])
def test_segment_list_extend_other(size):
    values = list(range(size))
    mapping = SegmentList(values)
    other = SegmentList(values)
    result = mapping.extend(other)
    assert result is None
    assert list(mapping) == values + values
    assert list(other) == values
    mapping._check()
    other._check()


def test_segment_list_extend_generator():
    mapping = SegmentList([1, 2])
    value = []
    mapping.extend(item for item in [value, value])
    assert list(mapping) == [1, 2, value, value]
    assert mapping[2] is mapping[3] is value
    mapping._check()


@pytest.mark.parametrize(
    'size, extra',
    [(0, 0), (0, 3), (3, 1), (10, 1), (100, 2), (2100, 2), (2100, 800)],
)
def test_segment_list_iadd(size, extra):
    values = list(range(size))
    mapping = SegmentList(values)
    original = mapping
    mapping += range(extra)
    assert mapping is original
    assert list(mapping) == values + list(range(extra))
    mapping._check()


@pytest.mark.parametrize('size', [0, 1, 7, 2100])
def test_segment_list_iadd_self(size):
    values = list(range(size))
    mapping = SegmentList(values)
    original = mapping
    mapping += mapping
    assert mapping is original
    assert list(mapping) == values + values
    mapping._check()


def test_segment_list_iadd_iterator_failure():
    mapping = SegmentList([1, 2])

    def failing():
        yield 3
        raise RuntimeError('iteration failed')

    with pytest.raises(RuntimeError, match='iteration failed'):
        mapping += failing()
    assert list(mapping) == [1, 2]
    mapping._check()


def test_segment_list_iadd_generator_aliases():
    value = []
    mapping = SegmentList(range(10))
    original = mapping
    mapping += (item for item in [value, value])
    assert mapping is original
    assert list(mapping) == list(range(10)) + [value, value]
    assert mapping[-1] is mapping[-2] is value
    mapping._check()
