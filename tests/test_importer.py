import sys


def test_yaml_import(sys_path_input):
    """
    We can import a linkml yaml schema as if it were a module of pydantic models
    """

    import linkml_pydantic  # noqa: F401, I001

    from schema_module import kitchen_sink  # noqa: I001

    # the test is basically that we can import the module from the yaml file.
    # tests for model correctness are in pythongen
    assert kitchen_sink.__package__ == "schema_module"
    assert kitchen_sink.__name__ == "schema_module.kitchen_sink"
    assert "schema_module.kitchen_sink" in sys.modules

    from schema_module.kitchen_sink import Person
