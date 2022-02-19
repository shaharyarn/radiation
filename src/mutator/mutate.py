import copy
from itertools import chain
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Sequence,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
)

import parso

T = TypeVar("T", bound=Type[parso.tree.NodeOrLeaf])
MutationFunction = Callable[[T], Sequence[T]]


class Mutation(TypedDict):
    name: str
    mutation_function: MutationFunction


TypeToMutations = Dict[str, List[Mutation]]


def mutate_node_or_leaf(
    node: parso.tree.NodeOrLeaf, type_to_mutations: TypeToMutations
) -> Iterable[Tuple[parso.tree.NodeOrLeaf, str]]:
    return (
        (mutated_node, mutation["name"])
        for mutate_on, mutations in type_to_mutations.items()
        if node.type == mutate_on
        for mutation in mutations
        for mutated_node in mutation["mutation_function"](copy.deepcopy(node))
    )


def node_mutations(
    node: parso.tree.NodeOrLeaf, type_to_mutations: TypeToMutations
) -> Iterable[Tuple[parso.tree.NodeOrLeaf, str]]:
    if isinstance(node, parso.tree.Leaf):
        return mutate_node_or_leaf(node, type_to_mutations)

    assert isinstance(node, parso.tree.BaseNode)
    mutations = []
    for index, child in enumerate(node.children):
        for mutation, name in node_mutations(child, type_to_mutations):
            node_copy = copy.deepcopy(node)
            node_copy.children[index] = mutation
            mutations.append((node_copy, name))
    return chain(mutations, mutate_node_or_leaf(node, type_to_mutations))


def code_mutations(
    code: str, type_to_mutations: TypeToMutations
) -> Iterable[Tuple[str, str]]:
    m = parso.parse(code=code)
    return (
        (mutation.get_code(), name)
        for mutation, name in node_mutations(m, type_to_mutations)
    )
