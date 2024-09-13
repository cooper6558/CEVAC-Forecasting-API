# Power Forecasting with LSTMs
The summer of 2020, I was tasked with designing machine learning models that
would forecast power consumption in different buildings for Clemson University.
Now, this is a time series analysis problem, so of course the first thing to
try would be multiple variations of ARIMA. In particular, I was interested in
ARIMAX, which is a variation of ARIMA that allows exogenous regressors. I had
some good results with this, but I struggled to match all possible cases, such
as weekends or special events. After trying a few different approaches, I
settled on my own implementation of an LSTM.  
_Note, while I detail the concepts behind my model, I do not provide actual
code, as I believe every specific implementation would be different, so my code
may not be what you need. However, you should be able to follow along and code
the concepts yourself with whatever libraries you prefer._

## The Concept of A Recurrent Neural Network
A classical neural network is pretty simple: you feed it some input tensor, and
it aims for a target output, adjusting the weights throughout the training data
to decrease the loss. A recurrent neural network is similar, but it retains an
internal state between samples. An example might be if a recurrent neural
network is trained on a video. One input might be a frame from the video, which
generates an output from the network, but also updates some internal state.
The next input is the next frame, but the previous state of the network is
saved, and so the output is dependent on the current frame as well as all
previous frames. Now, there are some [problems](
https://medium.com/datadriveninvestor/how-do-lstm-networks-solve-the-problem-of-vanishing-gradients-a6784971a577
) with classical neural networks. Generally, they have trouble remembering
information for more than a few time steps. LSTMs solve this problem, making
them perfect for time series data where current time steps may depend on
historical events. So, the LSTM became the core of my approach.

## Exogenous Regressors with Time Series Analysis
For any given time step, there are likely factors other than the previous time
step that play into the predictions. For power consumption, I found the main
factors to be occupancy, temperature, and cloud coverage. So, in order to
produce power consumption forecasts, we needed forecasts for these other
variables first.  
The model also benefits from knowing what time of day and year it is, and
knowing whether it is a weekend. So, part of the model will involve generating
these regressors from the date time index of the given data. The weekend data
will simply be a binary indicator. As for time of day and year, there will be
two separate signals for each; a sine signal and a cosine signal, with periods
the length of a day and year, respectively. Mathematically, given the sine of
a value and the cosine a value, there can exist no more than one point per
cycle satisfying both terms. So, this will allow the model to keep track of
time.  
To recap here, the variables available to the model from the previous time step
now include, for a total of 9 features:
- Power Consumption
- Temperature
- Cloud Coverage
- Occupancy
- `sin(2*pi*day_of_year/365)`
- `cos(2*pi*day_of_year/365)`
- `sin(2*pi*time_of_day/24)`
- `cos(2*pi*time_of_day/24)`
- Weekend

Now, this data may not be hourly. It is important that you group your
observations by hour, and then take the mean of each hour. This way, the
observations "line up" in a data frame.

## Dealing with Missing Data
When your model depends on forecasted regressors, there is bound to be missing
data. The package scikit-learn (`pip install sklearn`) has a tool called
`IterativeImputer` that can estimate and fill in missing data. I used this
tool to make the model more robust. It might not be the latest and greatest
machine learning algorithm, but it's really just a helper for our main
algorithm, as we can't afford to have any missing data fed into the LSTM.

## Differencing
One important thing to do with time series forecasting is to remove any trends
in your data. It is much easier for the model to learn when it doesn't have to
learn trends or cycles. There probably won't be long term trends present in
power forecasting data, but there will almost certainly be cycles. So, we need
a way to eliminate this.  
Differencing is a common strategy; that is, subtracting each observation in the
target variable from its previous observation. If you have a linear trend, this
has the same effect as taking the first derivative of a linear function, where
the trend is no longer present. However, cyclical trends are a bit more
complicated. To remove a cyclical trend, you don't difference from the
previous observation - you have to difference by the length of the cycle. For
example, if the cycle is daily, and the observations are hourly, you need to
difference by 24 hours.  
So, what is the cycle length of power data? One might say it is daily, where
you get power spikes at midday, and then it drops at night. However, the
weekends actually make it more of a weekly cycle. I found treating it this way
to be more effective, so part of the model involves subtracting from each
observation the value exactly one week prior. This removed the trends, but
introduced other problems.  
When the model was predicting the difference in power consumption, the other
variables lost a lot of weight because there isn't necessarily a strong
correlation between, say, current temperature, and how much more power is now
being used than was being used one week ago. The model needs access to last
week's temperature as well, but it may have forgotten this information along
the way. So, to solve this problem, I differenced all four variables.

## Standardizing
Finally, to train any machine learning model, they tend to converge better if
the data is standardized. To do this, simply subtract the mean and divide by
the standard deviation.  
The important part to remember here is that you have to do everything to your
testing data and "production" data that you do to your training data. The model
learns patterns assuming the data has been standardized by the mean and
standard deviation of the training data, so these two values must be stored in
a file for long term storage if you want to distribute the model.

## The LSTM Itself
All of the previous stuff was really just getting the data ready to put in a
neural network. The architecture can vary from case to case, depending on what
you find to give the best results. However, you need to meet the following
basic requirements.
- Nine features for the input vector
- One output feature: future power consumption; this can be done with a single
dense layer with one output
- Dropout layer: this is required to prevent LSTMs from overfitting. For me, a
rate of 0.4 worked well, but you will need to try different values for each
dataset.

## Putting it all together
This makes up the architecture that I have found to work well for power
forecasting. It is robust to missing data, it handles events well because of
the regressors, and due to the nature of the differencing, it effectively
handles cycles, even when they are present on only some days of the week. So,
to recap, the full implementation takes the following steps to make a forecast.
1. Get forecasts of temperature, cloud coverage, and occupancy data.
2. Fill in any missing data from these forecasts using scikit-learn, group them
by hour, and average them.
3. Difference all of the variables.
4. Add indicators for time of year, time of day, and whether it's a weekend.
5. Standardize the data.
6. Feed this data set into an LSTM, one window at a time.
7. Reverse the standardizing, and reverse the differencing.
8. Do this for each sequential time step you would like to predict.

When testing the model with a one week forecast of 168 predictions, on power
data on the order of 300 kW, I got mean squared errors as low as 123 kW^2. 
