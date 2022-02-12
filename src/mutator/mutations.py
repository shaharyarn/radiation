import copy
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, List

import parso

from .mutate import MutationFunction, T, TypeToMutations

types_to_mutations: TypeToMutations = defaultdict(lambda: list())


def mutate_on(
    mutate_on: T,
) -> Callable[[MutationFunction], MutationFunction]:
    def wrapper(f: MutationFunction) -> MutationFunction:
        @wraps(f)
        def inner_wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            return f(*args, **kwargs)

        types_to_mutations[mutate_on].append(inner_wrapper)
        return inner_wrapper

    return wrapper


@mutate_on(parso.python.tree.Number)
def change_relative_values(
    node: parso.python.tree.Number,
) -> List[parso.python.tree.Number]:
    values = [1, 1000, -1, -1000]
    mutated_nodes = []
    for value in values:
        copied_node = copy.deepcopy(node)
        copied_node.value = str(int(copied_node.value) + value)
        mutated_nodes.append(copied_node)
    return mutated_nodes
