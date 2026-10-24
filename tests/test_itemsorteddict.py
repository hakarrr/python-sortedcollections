"Test sortedcollections.ItemSortedDict"

import copy

import pytest

from sortedcollections import ItemSortedDict


def key_func(key, value):
    return key


def value_func(key, value):
    return value


alphabet = 'abcdefghijklmnopqrstuvwxyz'


def test_init():
    temp = ItemSortedDict(key_func)
    temp._check()


def test_init_args():
    temp = ItemSortedDict(key_func, enumerate(alphabet))
    assert len(temp) == 26
    assert temp[0] == 'a'
    assert temp[25] == 'z'
    assert temp.keys()[4] == 4
    temp._check()


def test_init_kwargs():
    temp = ItemSortedDict(key_func, a=0, b=1, c=2)
    assert len(temp) == 3
    assert temp['a'] == 0
    assert temp.keys()[0] == 'a'
    temp._check()


def test_getitem():
    temp = ItemSortedDict(value_func, enumerate(reversed(alphabet)))
    assert temp[0] == 'z'
    assert temp.keys()[0] == 25
    assert list(temp) == list(reversed(range(26)))


def test_delitem():
    temp = ItemSortedDict(value_func, enumerate(reversed(alphabet)))
    del temp[25]
    assert temp.keys()[0] == 24


def test_delitem_error():
    temp = ItemSortedDict(value_func, enumerate(reversed(alphabet)))
    with pytest.raises(KeyError):
        del temp[-1]


def test_setitem():
    temp = ItemSortedDict(value_func, enumerate(reversed(alphabet)))
    temp[25] = '!'
    del temp[25]
    iloc = temp.keys()
    assert iloc[0] == 24
    temp[25] = 'a'
    assert iloc[0] == 25


def test_copy():
    temp = ItemSortedDict(value_func, enumerate(reversed(alphabet)))
    that = temp.copy()
    assert temp == that
    assert temp._key != that._key


def test_deepcopy():
    temp = ItemSortedDict(value_func, enumerate(reversed(alphabet)))
    that = copy.deepcopy(temp)
    assert temp == that
    assert temp._key != that._key


def test_update():
    temp = ItemSortedDict(lambda key, value: value)
    for index, letter in enumerate(alphabet):
        pair = {index: letter}
        temp.update(pair)


@pytest.mark.parametrize('via_list', [False, True])
def test_deepcopy_recursive_value(via_list):
    mapping = ItemSortedDict(lambda key, value: key)
    mapping['self'] = [mapping] if via_list else mapping
    clone = copy.deepcopy(mapping)
    assert clone is not mapping
    assert clone._func is mapping._func
    assert (clone['self'][0] if via_list else clone['self']) is clone
    clone._check()
    clone['other'] = 1
    clone._check()
    assert 'other' not in mapping


def test_deepcopy_shared_values_and_outer_memo():
    shared = []
    mapping = ItemSortedDict(lambda key, value: key, a=shared, b=shared)
    clone, copied_shared, repeated_clone = copy.deepcopy(
        [mapping, shared, mapping]
    )
    assert clone is repeated_clone
    assert clone['a'] is clone['b'] is copied_shared
    assert copied_shared is not shared
    clone['a'].append(1)
    assert shared == []
    clone._check()


def test_deepcopy_recursive_key():
    class Key:
        pass

    key = Key()
    mapping = ItemSortedDict(lambda key, value: 0)
    key.mapping = mapping
    mapping[key] = key
    clone = copy.deepcopy(mapping)
    copied_key = next(iter(clone))
    assert copied_key is not key
    assert copied_key.mapping is clone
    assert clone[copied_key] is copied_key
    clone._check()


def test_deepcopy_empty_subclass():
    class Subclass(ItemSortedDict):
        pass

    mapping = Subclass(lambda key, value: key)
    clone = copy.deepcopy(mapping)
    assert type(clone) is Subclass
    assert clone._func is mapping._func
    assert not clone
    clone['new'] = 1
    clone._check()
    assert not mapping


def test_deepcopy_mutually_recursive_mappings():
    first = ItemSortedDict(lambda key, value: key)
    second = ItemSortedDict(lambda key, value: key)
    first['second'] = second
    second['first'] = first
    clone = copy.deepcopy(first)
    assert clone['second'] is not second
    assert clone['second']['first'] is clone
    clone._check()
    clone['second']._check()
