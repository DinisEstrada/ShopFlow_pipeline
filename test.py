import pandas as pd

customers = pd.read_csv("data/raw/customers.csv")
print(customers[customers["id"] == 240])
