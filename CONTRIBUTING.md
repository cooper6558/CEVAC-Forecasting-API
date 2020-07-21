# Contributing to the CEVAC Forecasting API
## Extending `power_forecasting`
### Adding an Architecture
1. Add a hidden module to the architectures package by prepending the file name
with an underscore. For example, `power_forecasting/architectures/_lstm.py` is
the file storing the LSTM architecture. Module names are `lower_case`.

2. In that new file, `from power_forecasting.architectures import Architecture`

3. Create a new class by the name of your architecture, inheriting the
Architecture class you just imported. Class names are CamelCase, or UPPERCASE
if it is an acronym.

4. The constructor for this new class should take a string, representing the
name of the building to be predicted, as an argument (after `self`, of course).

5. Call the super constructor, passing the building name. This will store the
directory in which all trained models for that building are saved, in the
string `self.path`.

6. Within this building's directory, your architecture's files are stored under
a sub directory with the lowercase name of your architecture. Use this to load
any files you need. For example,
`self.model = pickle.load(f"{self.path}lstm/model.pkl")`.
This completes the class constructor.

7. The class needs a `predict` method. It will return a DateTime indexed pandas
Series, and take the following arguments:
    - self, as an instance of your class
    - historical data, as a pandas DataFrame
    - future data, as a pandas DataFrame
    - a verbosity argument, as a Boolean

8. Open `power_forecasting/architectures/__init__.py` and export your class. To
do this, import your class name from your module. For example, the line
`from power_forecasting.architectures._lstm import LSTM` exports the LSTM
class.

9. Store all files containing pretrained models in the
[Forecasting Models Repository](
https://gitlab.clemson.edu/cevac/research/cevac-forecasting-models), with the
convention `/building_name/architecture/`. For example, all files required by
the LSTM for the Watt center are stored in `/watt/lstm/` in this repository.

### Adding a Building
1. Add a hidden module to the buildings package by prepending the file name
with an underscore. For example, `power_forecasting/buildings/_watt.py`
provides support for the Watt center. Module names are `lower_case`.

2. In that file, `from power_forecasting.buildings import Building`

3. Create a new class by the name of your building, inheriting the Building
class you just imported. Class names are CamelCase, or UPPERCASE if it is an
acronym.

4. The constructor takes no arguments, calls the super constructor, and sets
`self.name` to the name of the building (with capitalization the same as class
names).

5. To use architectures on this building that require occupancy forecasts (such
as LSTM), add `from occupancy_forecasting import buildings` to the top of the
file, and in the constructor, set `self.occupancy_building` to the
corresponding building class from the occupancy API. For example, the `Watt`
constructor has `self.occupancy_building = buildings.Watt`. (This step is not
necessary if you don't use architectures on that building that require
occupancy).

### Adding Data
The `Predictor` class automatically collects data specific to a `building`, and
passes that data to an `architecture` to produce a forecast. You may design an
architecture that needs more variables than are currently available.

1. Open `power_forecasting/_load_data.py`, and write a function that returns a
pandas Series. This function must behave as follows.
    - Arguments will include start and end dates provided as pandas TimeStamps.
    - If the data is building specific, it can take a building object as well.
    (The name of a building as a string is available as `Building.name`)
    - The function will produce an hourly DateTime indexed Series between and
    including the given start & end dates. The index must be consecutive; that
    is, missing data for a given hour should be `NaN`, not just a missing row.
    - Some functions are available in this file to help with that, such as
    `group_by_hour` and `get_sql`. You can also add your own helper functions
    as you need.

2. The `load_regressors` function concatenates a list of Series objects
starting on line 64. At the **end** of this list, add a call to your function,
giving it whatever arguments it needs. Then, add the name of your column to
this function's docstring.

## Extending `occupancy_forecasting`
