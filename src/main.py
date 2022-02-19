import click

from .mutator import code_mutations, types_to_mutations


@click.command()
@click.argument("file_name")
def main(file_name: str):
    with open(file_name) as f:
        code = f.read()

    for index, (mutated_code, name) in enumerate(
        code_mutations(code, types_to_mutations)
    ):
        print(f"----------------mutant {index} {name}-------------")
        print(mutated_code)


if __name__ == "__main__":
    main()
