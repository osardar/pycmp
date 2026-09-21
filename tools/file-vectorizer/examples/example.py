"""Owned fixture for the CLI quickstart; ingestion does not run this file."""


def total_positive(values):
    return sum(value for value in values if value > 0)
