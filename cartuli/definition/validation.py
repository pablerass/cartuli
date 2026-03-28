import json

from jsonschema import Draft202012Validator, RefResolver
from referencing import Registry


def validator() ->

def is_valid(definition: dict, validator: Draft202012Validator) -> bool:
    return validator.validate(definition)
