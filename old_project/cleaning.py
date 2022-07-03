import numpy as np
import pandas as pd
import seaborn
from matplotlib import pyplot as plt

df = pd.read_csv("Data/houses_dirty.csv")
df = df.iloc[:,1:]

def clean_column_one(price_tag):
    if price_tag[0] == "$":
        price = price_tag[1:].replace(".", "").replace(",", "")
        price = float(price)
    else:
        price = price_tag[2:].replace(",", ".")
        price = float(price) * 29302
    return price
def clean_column_two(string):
    try:
        msq = string.split()
        msq = msq[0].replace(",", "")
        return float(msq)
    except KeyError:
        return np.nan
df.columns = ['price', 'm^2', 'rooms', 'location', 4, 5]
df['rooms'] = df['rooms'].apply(lambda x: int(x.split()[0]))
df.iloc[:,3:] = df.iloc[:,3:].astype(str).applymap(lambda x: x.lower().strip())
df.iloc[:,0] = df.iloc[:,0].apply(lambda x: clean_column_one(x)).astype(np.float32)
df.iloc[:,1] = df.iloc[:,1].apply(lambda x: clean_column_two(x)).astype(np.float32)
def check_for_odd_type():
    for i, value in enumerate(df.iloc[:,0]):
        if isinstance(value, str):
            print(f"{value} is of type {type(value)} at index {i}")
        else:
            if i%10==0:
                print(f"index {i}, with value {value}")
#check_for_odd_type()

df = df.sort_values(by='price', axis=0)
mask = df.iloc[:,1] > 1000
df = df.drop(index=df.index[mask])
df = df.reset_index(drop=True)

comunas = ["Colina, Lampa, Til Til, Cordillera, Puente Alto, Pirque, Puente Alto, "
           "San José de Maipo, Maipo, San Bernardo, Buin,  Calera de Tango,"
           "Paine, San Bernardo, Melipilla, Alhué, Curacaví, María Pinto,"
           "Melipilla, San Pedro, Cerrillos, Cerro Navia, Conchalí,"
           "El Bosque, Estación Central, Huechuraba, Independencia,"
           "La Cisterna, La Granja, La Florida, La Pintana, La Reina, "
           "Las Condes, Lo Barnechea, Lo Espejo, Lo Prado, Macul, Maipú,"
           "Ñuñoa, Pedro Aguirre Cerda, Peñalolén, Providencia, Pudahuel, "
           "Quilicura, Quinta Normal, Recoleta, Renca, San Miguel, San Joaquín, "
           "San Ramón, Vitacura, El Monte, Isla de Maipo, Padre Hurtado, Peñaflor Talagante, Santiago"]
[comunas] = [comuna.lower().split(",") for comuna in comunas]
comunas = {comuna.strip() for comuna in comunas}

df.iloc[:,3] = df.iloc[:,3:].apply(lambda x: ' '.join([str(c).lower().strip() for c in x]), axis=1)
df = df.drop(columns=[4,5], axis=0)

for i, value in enumerate(df['location']):
    values = []
    for comuna in comunas:
        if comuna in value:
            values.append(comuna)
    df.iloc[i,3] = values[-1].strip() if len(values) != 0 else pd.NA

print(df['location'].unique())
mask_index = df['location'] == 'peñalolén'
ax = df[mask_index].plot(y='price', legend=False, kind='line')
ax2 = ax.twinx()
df[mask_index].plot(y='m^2', ax=ax2, legend=False, kind='line', color="r")
ax.grid(True)
ax.figure.legend()
plt.show()

cat_comunas = {comuna: i for i, comuna in enumerate(df['location'].unique())}
df['location'] = df['location'].apply(lambda x: cat_comunas[x])
seaborn.heatmap(df.corr())
plt.show()






