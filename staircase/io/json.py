import json

import numpy as np
import pandas as pd


def _get_class_from_name(name):
    from staircase import Stairs
    from staircase.core.stats.distribution import ECDF, Fractiles, Percentiles

    return {
        "Stairs": Stairs,
        "Fractiles": Fractiles,
        "Percentiles": Percentiles,
        "ECDF": ECDF,
    }[name]


def _get_orient(series):
    if isinstance(series.index, pd.TimedeltaIndex):
        orient = "index"
    else:
        orient = "table"
    return orient


class StairsJSONEncoder(json.JSONEncoder):
    def default(self, obj_to_encode):
        """Pandas and Numpy have some specific types that we want to ensure
        are coerced to Python types, for JSON generation purposes. This attempts
        to do so where applicable.
        """
        # Pandas dataframes have a to_json() method, so we'll check for that and
        # return it if so.
        if isinstance(obj_to_encode, pd.Series):
            orient = _get_orient(obj_to_encode)
            return obj_to_encode.to_json(orient=orient, date_unit="ns")

        if hasattr(obj_to_encode, "to_json"):
            return obj_to_encode.to_json()

        if isinstance(obj_to_encode, np.integer):
            return int(obj_to_encode)

        if isinstance(obj_to_encode, np.floating):
            return float(obj_to_encode)

        return super().default(obj_to_encode)


class StairsJSONDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs["object_hook"] = self.object_hook
        super().__init__(**kwargs)

    def object_hook(self, obj):

        return _get_class_from_name(obj["class"]).from_values(
            initial_value=obj["initial_value"],
            closed=obj["closed"],
            values=self._read_series(obj["values"], orient=obj["series_orient"]),
        )

    @staticmethod
    def _read_series(values, orient):
        kwargs = {"orient": orient}
        if orient == "index":
            kwargs["convert_axes"] = False
        obj = pd.read_json(values, **kwargs)
        if isinstance(obj, pd.DataFrame):
            obj = obj.iloc[:, 0]
        if orient == "index":
            obj.index = pd.TimedeltaIndex(obj.index)
        return obj


def to_json(self):
    """Convert the Stairs object *self* to a JSON string."""

    return json.dumps(
        {
            "class": type(self).class_name,
            "series_orient": _get_orient(self.step_values),
            "initial_value": self.initial_value,
            "closed": self.closed,
            "values": self.step_values,
        },
        cls=StairsJSONEncoder,
    )


def read_json(string):
    """Converts a JSON string to a Stairs instance"""
    return json.loads(string, cls=StairsJSONDecoder)
