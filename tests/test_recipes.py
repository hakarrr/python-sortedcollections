"Test sortedcollections.recipes"

import copy
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


@pytest.mark.parametrize('values', [[], [3, 1, 2], list(range(2500, -1, -1))])
@pytest.mark.parametrize('copier', [lambda value: value.copy(), copy.copy])
def test_segment_list_shallow_copy(values, copier):
    original = SegmentList(values)
    duplicate = copier(original)
    assert isinstance(duplicate, SegmentList)
    assert duplicate is not original
    assert list(duplicate) == values
    duplicate.append('new')
    assert list(original) == values
    duplicate._check()
    original._check()


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize('values', [[], [3, 1, 2], list(range(2500, -1, -1))])
def test_segment_list_pickle(values, protocol):
    original = SegmentList(values)
    duplicate = pickle.loads(pickle.dumps(original, protocol))
    assert isinstance(duplicate, SegmentList)
    assert duplicate is not original
    assert list(duplicate) == values
    duplicate.append('new')
    duplicate[0] = 'changed'
    del duplicate[-1]
    assert list(original) == values
    duplicate._check()
    original._check()


def test_segment_list_copy_preserves_element_sharing():
    element = [1]
    original = SegmentList([element, element])
    shallow = copy.copy(original)
    deep = copy.deepcopy(original)
    assert shallow[0] is element
    assert shallow[1] is element
    assert deep[0] == element
    assert deep[0] is not element
    assert deep[0] is deep[1]
    deep[0].append(2)
    assert element == [1]
    assert deep[1] == [1, 2]
    deep._check()
    shallow._check()
    original._check()
