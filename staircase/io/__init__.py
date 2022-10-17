from staircase.io.json import read_json, to_json


def add_methods(cls):
    cls.to_json = to_json
