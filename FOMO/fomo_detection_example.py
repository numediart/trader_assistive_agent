# from FOMO.fomo_utils import download_market
# import sys
#
# download_market("AAPL", "1mo", "1h")
# sys.exit(0)



from fomo_detectors import FOMO_Detector_v0
import pandas as pd
from datetime import datetime
import os

path = os.path.join("FOMO", "data")
path = os.path.join(path, "AAPL_1mo_1h.csv")
data = pd.read_csv(path)

fomo_detector = FOMO_Detector_v0(incr_per=5., num_days=10)

for index, row in data.iterrows():
    value = row['Close']
    date = datetime.fromisoformat(row['Datetime'])
    is_fomo, increase, old_value = fomo_detector.process(date, value)
    print("{} - {} - {} - {}% - {}".format(date, value, is_fomo, increase, old_value))
