from kirkham.parser import KirkhamParser


def main():
    """Demonstrate the English Grammar Parser.

    Shows example usage of the Parser class with its clean API:
    parse(), explain(), to_json(), show()
    """
    parser = KirkhamParser()

    # Example sentences
    examples = [
        "The very good children were given toys.",
        "She got promoted yesterday.",
    ]

    print("\n" + "=" * 70)
    print("ENGLISH GRAMMAR PARSER")
    print("Based on Samuel Kirkham's English Grammar (1829)")
    print("=" * 70)

    # Demonstrate formatted output using explain()
    for sentence in examples:
        print(f"\n\nSENTENCE: {sentence}")
        print(parser.explain(sentence))

    # Demonstrate JSON output using show()
    print("\n\n" + "=" * 70)
    print("JSON OUTPUT EXAMPLE")
    print("=" * 70)
    parser.show(examples[0], json_only=True)


if __name__ == "__main__":
    main()
