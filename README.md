# linkml-pydantic

Runtime library for using linkml pydantic models.

Placeholder package pending a more complete refactoring of linkml to not have a bajillion dependencies

## Usage

If you have `linkml_pydantic` imported, you can import any linkml schema directly from the yaml file

eg. if you have a package like:

```python
mypackage
├── __init__.py
└── kitchen_sink.yaml
```

then you can import from `kitchen_sink.yaml` as if it were a python file:

```python
from mypackage import kitchen_sink
from mypackage.kitchen_sink import Person
```


## TODO

- [ ] Handle imported modules - see `nwb_linkml`'s providers and modified generators
- [ ] Reverse synchronization - sync linkml schema from pydantic models
- [ ] Integrate with IDEs/type checkers - make it appear as if the module really exists and can be introspected