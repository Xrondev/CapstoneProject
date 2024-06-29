import pandas as pd
from neuralforecast.models import Autoformer, iTransformer
from neuralforecast.core import NeuralForecast

# --------LOAD DATA-----------
price_data_path = '../../data/price.csv'
price_data = pd.read_csv(price_data_path)
price_data['ds'] = pd.to_datetime(price_data['ds'])
print(price_data.head(5))

# TODO: integrate the LLM processed data with the price data

Y_df = pd.DataFrame(price_data)
n_time = len(Y_df['ds'].unique())
val_size = int(0.2 * n_time)
test_size = int(0.2 * n_time)

# ----------MODEL-------------

horizon = 7  # 7 hours per day

models = [Autoformer(
    h=horizon,  # forecasting horizon
    input_size=horizon * 7,  # input size
    max_steps=1000,
    val_check_steps=50,
    early_stop_patience_steps=5,

)]

nf = NeuralForecast(
    models=models,
    freq='H'  # hourly frequency
)

Y_hat_df = nf.cross_validation(df=Y_df,
                               val_size=val_size,
                               test_size=test_size,
                               n_windows=None)

# ----------- SAVE --------------
nf.save(path='./ckpts/',
        save_dataset=True,
        overwrite=True)

# ----------- PLOT --------------
print(Y_hat_df.head(5))
Y_hat_df.reset_index(inplace=True)
Y_hat_df.rename(columns={'y': 'actual'}, inplace=True)
from utilsforecast.plotting import plot_series

plot_series(Y_df, Y_hat_df.loc[:, Y_hat_df.columns != 'cutoff'], max_insample_length=300)
