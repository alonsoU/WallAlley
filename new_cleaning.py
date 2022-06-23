import pandas as pd

columns = ["oferta","propiedad","monto","moneda","direccion", \
    "inmobiliaria","comentario","metros_quad","n_dormitorios","n_baños"]
raw = pd.read_csv("./Data/real_estate_data_raw.csv")
raw.columns = columns

print(len(raw))

raw = raw.drop_duplicates()
raw.dropna(subset=["monto", "moneda", "direccion", "metros_quad"])
raw.reset_index()
print(len(raw))

mask = [not number.isnumeric() for number in raw["monto"]] # rows to eliminate
print(raw.loc[mask,"monto"])
mask = raw.index[mask]
raw = raw.drop(index=mask)
raw.reset_index()
print(len(raw))

print(raw)
print(raw.describe())
raw = raw.convert_dtypes()
print(raw.dtypes)