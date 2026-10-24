"Test sortedcollections.ValueSortedDict"

import copy
import pickle

import pytest

from sortedcollections import ValueSortedDict


def identity(value):
    return value


alphabet = 'abcdefghijklmnopqrstuvwxyz'


def test_init():
    temp = ValueSortedDict()
    temp._check()


def test_init_args():
    temp = ValueSortedDict(enumerate(alphabet))
    assert len(temp) == 26
    assert temp[0] == 'a'
    assert temp[25] == 'z'
    assert temp.keys()[4] == 4
    temp._check()


def test_init_kwargs():
    temp = ValueSortedDict(None, a=0, b=1, c=2)
    assert len(temp) == 3
    assert temp['a'] == 0
    assert temp.keys()[0] == 'a'
    temp._check()


def test_getitem():
    temp = ValueSortedDict(identity, enumerate(reversed(alphabet)))
    assert temp[0] == 'z'
    assert temp.keys()[0] == 25
    assert list(temp) == list(reversed(range(26)))


def test_delitem():
    temp = ValueSortedDict(identity, enumerate(reversed(alphabet)))
    del temp[25]
    assert temp.keys()[0] == 24


def test_delitem_error():
    temp = ValueSortedDict(identity, enumerate(reversed(alphabet)))
    with pytest.raises(KeyError):
        del temp[-1]


def test_setitem():
    temp = ValueSortedDict(identity, enumerate(reversed(alphabet)))
    temp[25] = '!'
    del temp[25]
    assert temp.keys()[0] == 24
    temp[25] = 'a'
    assert temp.keys()[0] == 25


def test_copy():
    temp = ValueSortedDict(identity, enumerate(reversed(alphabet)))
    that = temp.copy()
    assert temp == that
    assert temp._key != that._key


def test_pickle():
    original = ValueSortedDict(identity, enumerate(reversed(alphabet)))
    data = pickle.dumps(original)
    duplicate = pickle.loads(data)
    assert original == duplicate


class Negater:
    def __call__(self, value):
        return -value

    def __repr__(self):
        return 'negate'


def test_repr():
    temp = ValueSortedDict(Negater())
    assert repr(temp) == 'ValueSortedDict(negate, {})'


def test_update():
    temp = ValueSortedDict()
    for index, letter in enumerate(alphabet):
        pair = {index: letter}
        temp.update(pair)


class ConstantKey:
    def __call__(self, value):
        return 0


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize('via_list', [False, True])
def test_pickle_recursive_value(protocol, via_list):
    mapping = ValueSortedDict(ConstantKey())
    mapping['self'] = [mapping] if via_list else mapping
    clone = pickle.loads(pickle.dumps(mapping, protocol=protocol))
    assert clone is not mapping
    assert (clone['self'][0] if via_list else clone['self']) is clone
    clone['other'] = []
    del clone['other']
    assert 'other' not in mapping
    clone._check()


@pytest.mark.parametrize('via_list', [False, True])
def test_deepcopy_recursive_value(via_list):
    mapping = ValueSortedDict(ConstantKey())
    mapping['self'] = [mapping] if via_list else mapping
    clone = copy.deepcopy(mapping)
    assert clone is not mapping
    assert clone._func is not mapping._func
    assert (clone['self'][0] if via_list else clone['self']) is clone
    clone['other'] = []
    del clone['other']
    clone._check()


def test_deepcopy_shared_values():
    shared = [1]
    mapping = ValueSortedDict(ConstantKey(), a=shared, b=shared)
    clone, value = copy.deepcopy([mapping, shared])
    assert clone['a'] is clone['b'] is value
    assert value is not shared
    value.append(2)
    assert shared == [1]
    clone._check()


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_mutually_recursive_mappings(protocol):
    first = ValueSortedDict(ConstantKey())
    second = ValueSortedDict(ConstantKey())
    first['second'] = second
    second['first'] = first
    clone = pickle.loads(pickle.dumps(first, protocol=protocol))
    assert clone['second']['first'] is clone
    assert clone['second'] is not second
    clone._check()
    clone['second']._check()


def test_deepcopy_mutually_recursive_mappings():
    first = ValueSortedDict(ConstantKey())
    second = ValueSortedDict(ConstantKey())
    first['second'] = second
    second['first'] = first
    clone = copy.deepcopy(first)
    assert clone['second']['first'] is clone
    assert clone['second'] is not second
    clone._check()
    clone['second']._check()


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_sorted_values(protocol):
    mapping = ValueSortedDict(Negater(), a=1, b=3, c=2)
    clone = pickle.loads(pickle.dumps(mapping, protocol=protocol))
    assert list(clone) == ['b', 'c', 'a']
    clone['a'] = 4
    assert list(clone) == ['a', 'b', 'c']
    assert list(mapping) == ['b', 'c', 'a']
    clone._check()


def test_deepcopy_sorted_values():
    mapping = ValueSortedDict(Negater(), a=1, b=3, c=2)
    clone = copy.deepcopy(mapping)
    assert clone._func is not mapping._func
    assert list(clone) == ['b', 'c', 'a']
    clone['a'] = 4
    assert list(clone) == ['a', 'b', 'c']
    assert list(mapping) == ['b', 'c', 'a']
    clone._check()


class RecursiveKey:
    pass


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_recursive_key(protocol):
    key = RecursiveKey()
    mapping = ValueSortedDict(ConstantKey())
    key.mapping = mapping
    mapping[key] = key
    clone = pickle.loads(pickle.dumps(mapping, protocol=protocol))
    copied_key = next(iter(clone))
    assert copied_key is not key
    assert copied_key.mapping is clone
    assert clone[copied_key] is copied_key
    clone._check()


def test_deepcopy_recursive_key():
    key = RecursiveKey()
    mapping = ValueSortedDict(ConstantKey())
    key.mapping = mapping
    mapping[key] = key
    clone = copy.deepcopy(mapping)
    copied_key = next(iter(clone))
    assert copied_key is not key
    assert copied_key.mapping is clone
    assert clone[copied_key] is copied_key
    clone._check()


class ValueSortedDictSubclass(ValueSortedDict):
    pass


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_empty_subclass(protocol):
    mapping = ValueSortedDictSubclass()
    clone = pickle.loads(pickle.dumps(mapping, protocol=protocol))
    assert type(clone) is ValueSortedDictSubclass
    assert not clone
    assert clone._func is None
    clone.update(a=3, b=1)
    assert list(clone) == ['b', 'a']
    clone._check()


def test_deepcopy_empty_subclass():
    mapping = ValueSortedDictSubclass()
    clone = copy.deepcopy(mapping)
    assert type(clone) is ValueSortedDictSubclass
    assert not clone
    assert clone._func is None
    clone.update(a=3, b=1)
    assert list(clone) == ['b', 'a']
    clone._check()
