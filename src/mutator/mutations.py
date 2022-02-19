import copy
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, List

import parso.python.tree as tree

from .mutate import Mutation, MutationFunction, TypeToMutations

types_to_mutations: TypeToMutations = defaultdict(lambda: list())


def mutate_on(
    mutate_on: str, *, name=None
) -> Callable[[MutationFunction], MutationFunction]:
    def wrapper(f: MutationFunction) -> MutationFunction:
        @wraps(f)
        def inner_wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            return f(*args, **kwargs)

        types_to_mutations[mutate_on].append(
            Mutation(mutation_function=inner_wrapper, name=name or f.__name__)
        )
        return inner_wrapper

    return wrapper


@mutate_on("number")
def change_relative_values(
    node: tree.Number,
) -> List[tree.Number]:
    values = [1, 1000, -1, -1000]
    mutated_nodes = []
    for value in values:
        copied_node = copy.deepcopy(node)
        copied_node.value = str(eval(copied_node.value) + value)
        mutated_nodes.append(copied_node)
    return mutated_nodes


@mutate_on("if_stmt")
def set_if_to_keyword(node: tree.IfStmt) -> List[tree.IfStmt]:
    possible_keywords = {"True", "False"}

    for index, child in enumerate(node.children):
        if (
            isinstance(child, tree.Leaf)
            and child.type == "operator"
            and child.value == ":"
        ):
            end_if_index = index
            break
    old_condition = node.children[1:end_if_index]
    if len(old_condition) == 1 and isinstance(old_condition[0], tree.Keyword):
        possible_keywords.difference_update({old_condition[0].value})

    mutated_nodes = []
    node.children = [node.children[0]] + node.children[end_if_index:]
    for keyword in possible_keywords:
        copied_node = copy.deepcopy(node)
        copied_node.children.insert(
            1, tree.Keyword(keyword, start_pos=node.start_pos, prefix=" ")
        )
        mutated_nodes.append(copied_node)
    return mutated_nodes


@mutate_on("keyword")
def replace_true_and_false(
    node: tree.Keyword,
) -> List[tree.Keyword]:
    keyword_dict = {"True": "False", "False": "True"}
    if node.value in keyword_dict:
        node.value = keyword_dict[node.value]
        return [node]
    return []


@mutate_on("keyword")
def replace_break_and_continue(
    node: tree.Keyword,
) -> List[tree.Keyword]:
    keyword_dict = {"break": "continue", "continue": "break"}
    if node.value in keyword_dict:
        node.value = keyword_dict[node.value]
        return [node]
    return []


@mutate_on("comparison")
def not_on_is_and_in(
    node: tree.PythonNode,
) -> List[tree.PythonNode]:
    old_comp = node.children[1]
    if isinstance(old_comp, tree.Keyword) and old_comp.type == "keyword":
        new_comp_op = tree.PythonNode(type="comp_op", children=[])
        not_keyword = tree.Keyword("not", start_pos=old_comp.start_pos, prefix=" ")
        if old_comp.value == "is":
            new_comp_op.children = [node.children[1], not_keyword]
            node.children[1] = new_comp_op
            return [node]

        if old_comp.value == "in":
            new_comp_op.children = [not_keyword, node.children[1]]
            node.children[1] = new_comp_op
            return [node]

    elif isinstance(old_comp, tree.PythonNode) and old_comp.type == "comp_op":
        if (
            isinstance(old_comp.children[0], tree.Keyword)
            and old_comp.children[0].value == "is"
        ):
            node.children[1] == old_comp.children[0]
            return [node]

        if (
            isinstance(old_comp.children[1], tree.Keyword)
            and old_comp.children[1].value == "in"
        ):
            node.children[1] == old_comp.children[1]
            return [node]
    return []
