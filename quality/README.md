# Adding a new criterion

## Implementation
- Add a new file in `models/criterion/criterions/`
- Implement a model inheriting from `model.criterion.criterion.Criterion`
  - This model needs to have a `name` field, `info` static method and `evaluate` method (see `min_words` for an example)
- Implement a model inheriting from `model.criterion.criterion.CriterionRules`
  - This model needs to have a `get_or_create` static method (see `min_words`
    for an example)
- Add these two models to all the `__init__.py` files until `models/__init__.py`
- Add the models to `model/criterion/criterion_list.py`
- Add the models to `admin.py`

## Adding a criterion to the global quality
- Add the criterion through the `UsesCriterion` model
- The `name` corresponds to the `name` field of the model inheriting `Criterion` and `version` to whichever version of it you want
- `rules` is the primary key of the model inheriting `CriterionRules` wanted
