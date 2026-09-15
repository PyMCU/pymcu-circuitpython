def pytest_addoption(parser):
    parser.addoption(
        "--update-sizes",
        action="store_true",
        default=False,
        help="refresh tests/corpus/sizes.json from successful corpus builds",
    )
