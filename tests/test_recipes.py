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


@pytest.mark.parametrize('size', [0, 4])
@pytest.mark.parametrize('method', ['copy', 'shallow', 'deep', 'pickle'])
def test_indexable_dict_reconstruction(size, method):
    value = ['shared']
    original = IndexableDict((i, value) for i in range(size))
    if method == 'copy':
        restored = original.copy()
    elif method == 'shallow':
        restored = copy.copy(original)
    elif method == 'deep':
        restored = copy.deepcopy(original)
    else:
        restored = pickle.loads(pickle.dumps(original))
    assert type(restored) is IndexableDict
    assert restored.key is hash
    assert list(restored.items()) == list(original.items())
    assert restored is not original
    if size:
        assert restored[0] is restored[1]
        assert (restored[0] is value) == (method in ('copy', 'shallow'))
    restored[10] = ['new']
    assert 10 not in original
    assert list(restored.keys()) == sorted(restored, key=hash)
    restored._check()
    original._check()


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_indexable_dict_pickle_protocols(protocol):
    original = IndexableDict({3: 'three', 1: 'one'})
    restored = pickle.loads(pickle.dumps(original, protocol))
    assert type(restored) is IndexableDict
    assert restored == original
    assert restored.key is hash
    restored._check()


@pytest.mark.parametrize('size', [0, 4])
@pytest.mark.parametrize('method', ['copy', 'shallow'])
def test_indexable_set_copy(size, method):
    original = IndexableSet(range(size))
    restored = original.copy() if method == 'copy' else copy.copy(original)
    assert type(restored) is IndexableSet
    assert restored.key is hash
    assert list(restored) == list(original)
    assert restored is not original
    restored.add(10)
    assert 10 not in original
    assert list(restored) == sorted(restored, key=hash)
    restored._check()
    original._check()


@pytest.mark.parametrize('operation, expected', [
    ('difference', {1}),
    ('intersection', {2}),
    ('symmetric_difference', {1, 3}),
    ('union', {1, 2, 3}),
])
def test_indexable_set_algebra(operation, expected):
    original = IndexableSet([1, 2])
    restored = getattr(original, operation)([2, 3])
    assert type(restored) is IndexableSet
    assert set(restored) == expected
    assert restored.key is hash
    restored._check()
    assert set(original) == {1, 2}


def test_indexable_dict_union():
    original = IndexableDict({1: 'left', 2: 'shared'})
    merged = original | {2: 'right', 3: 'new'}
    reflected = {2: 'right', 3: 'new'} | original
    assert type(merged) is type(reflected) is IndexableDict
    assert merged == {1: 'left', 2: 'right', 3: 'new'}
    assert reflected == {1: 'left', 2: 'shared', 3: 'new'}
    assert merged.key is reflected.key is hash
    merged._check()
    reflected._check()
    assert original == {1: 'left', 2: 'shared'}


def test_indexable_recipes_keep_fixed_hash_key():
    with pytest.raises(TypeError):
        IndexableDict(lambda key: key, {1: 2})
    with pytest.raises(TypeError):
        IndexableSet([1], key=lambda key: key)
    mapping = IndexableDict(key='ordinary item')
    assert mapping['key'] == 'ordinary item'
    assert mapping.key is hash
