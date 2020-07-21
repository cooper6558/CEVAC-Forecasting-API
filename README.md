# Power Forecasting
API for power forecasting models developed with CEVAC.

## Installation
`pip install git+https://gitlab.clemson.edu/cevac/research/cevac-forecasting-api.git@master`  

This package requires
[CEVAC Python](https://gitlab.clemson.edu/cevac/CEVAC_python), and there are a
few ways to do this. I refer you to
[Bennett Meares](mailto:bmeares@clemson.edu) for more information.

## Usage
### `power_forecasting`
```shell script
$ pwd
>>> ~/
$ git clone https://gitlab.clemson.edu/cevac/research/cevac-forecasting-models
```
```python
"""
Example using the CEVAC Power Forecasting API.
"""

from power_forecasting import Predictor
from power_forecasting.buildings import Watt
from power_forecasting.architectures import LSTM
import pandas as pd
import os

os.environ["FORECAST_MODEL_DIR"] = "~/cevac-forecasting-models/"

predictor = Predictor(
    building=Watt,
    architecture=LSTM
)

future_range = pd.to_timedelta(1, unit="W")

predictor.forecast(
    future_range=future_range
)
```

## Advanced Installation Methods: SSH & Git Cloning
Alternatively, you can install via SSH. This is the recommended method if you
are comfortable with SSH, as you don't need to enter your username and password
every time you install or upgrade, and you can install without Clemson network
or VPN access. To do this, make sure you save your public key on your Clemson
GitLab account, and just replace `https` with `ssh` in the install command. If
you want to use a config file, `Hostname` is `gitlab.clemson.edu`, and `User`
is `git`. Your identity is determined by the key file you provide. In the
installation command, replace `git@gitlab.clemson.edu` with the value you set
for `Host`, i.e.  
`pip install git+ssh://[Host]/cevac/research/cevac-forecasting-api.git@master`  

Finally, you may simply `git clone` the whole thing, and install from there. Do
this if there is some obscure modification you need to make to the API. If
you're doing this, I assume you're savvy enough to not need me to explain it.