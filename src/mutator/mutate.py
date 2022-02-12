import copy
from itertools import chain
from typing import Callable, Dict, Iterable, List, Sequence, Type, TypeVar

import parso

T = TypeVar("T", bound=Type[parso.tree.NodeOrLeaf])
MutationFunction = Callable[[T], Sequence[T]]
TypeToMutations = Dict[Type[parso.tree.NodeOrLeaf], List[MutationFunction]]


def mutate_node_or_leaf(
    node: parso.tree.NodeOrLeaf, type_to_mutations: TypeToMutations
) -> Iterable[parso.tree.NodeOrLeaf]:
    return chain(
        *[
            mutation(copy.deepcopy(node))  # type: ignore
            for mutate_on, mutations in type_to_mutations.items()
            for mutation in mutations
            if isinstance(node, mutate_on)
        ]
    )


def node_mutations(
    node: parso.tree.NodeOrLeaf, type_to_mutations: TypeToMutations
) -> Iterable[parso.tree.NodeOrLeaf]:
    if isinstance(node, parso.tree.Leaf):
        return mutate_node_or_leaf(node, type_to_mutations)

    assert isinstance(node, parso.tree.BaseNode)
    mutations = []
    for index, child in enumerate(node.children):
        for mutation in node_mutations(child, type_to_mutations):
            node_copy = copy.deepcopy(node)
            node_copy.children[index] = mutation
            mutations.append(node_copy)
    return chain(mutations, mutate_node_or_leaf(node, type_to_mutations))


def code_mutations(code: str, type_to_mutations: TypeToMutations) -> Iterable[str]:
    m = parso.parse(code=code)
    return (mutation.get_code() for mutation in node_mutations(m, type_to_mutations))
