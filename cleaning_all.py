import numpy as np
import pandas as pd
import seaborn
from matplotlib import pyplot as plt
# print([num for num in ["1","2","c"] if num.isnumeric()])
prop = pd.read_csv("Data/all_house_data_raw.csv")
prop.columns = ['price', 'area', 'rooms', 'location', 4, 5, 6, "operation", "type"]

def slide_tags_slow(df, slide_size=2):
    for index, row in df.iterrows():
        mask = row.isna().values
        if not mask[-1]:
            continue # At least one extra space at the end
        for i, is_empty in enumerate(mask[::-1]):
            if not is_empty:
                slide_space = i
                break
        data = row[df.columns[~mask]][-slide_size:].values # data to be slid
        na_fill = np.full((slide_space), pd.NA)
        df.iloc[index,:] = np.concatenate((row.iloc[:len(mask)-(slide_space+slide_size)].values, na_fill, data))
def slide_tags(df, slide_size=2):
    # slide 'slide_size values of a row to the right of the dataframe.
    slide_indices = []
    last_mask = np.full((len(df.index)), True)
    len_col = len(df.columns)
    for i in range(len_col):
        mask = last_mask & df.iloc[:,-(i+1)].isna().values # boolean mask with uninterrupted NA values
        if mask.sum() == 0: # when intersection is all false, there is no more valiable data
            break
        slide_indices.append(df.index[mask])
        last_mask = mask
    max_gap = len(slide_indices)
    for i, indices in enumerate(slide_indices[::-1]):
        gap = max_gap-i
        slide = np.min([slide_size, len_col-gap]) # on a array slice, there is no more info when you extend the index
        # the index past the array's length.
        prev_data = df.iloc[indices, -slide-gap:len_col-gap]
        if not prev_data.empty:
            df.iloc[indices, -slide-gap+1:len_col-gap+1] = prev_data #sliding 'slide_size' values one column to the right
        df.iloc[indices, -slide-gap] = pd.NA

def clean_tofloat(price_tag):
    price_dot = price_tag.split(".")
    price_coma = price_tag.split(",")
    sep_diff = len(price_dot) - len(price_coma)
    if sep_diff == 0:
        if len(price_coma) == 1:
            price = float(price_tag)
        else:
            if price_coma[-1] in price_dot[-1]:  # ej: assert 23 in 434,23
                price = price_tag.replace(".", "").replace(",", ".")
            else:
                price = price_tag.replace(",", "")
    elif sep_diff > 1:
        price = price_tag.replace(".", "").replace(",", ".")
        price = float(price)
    elif sep_diff < -1:
        price = price_tag.replace(",", "")
        price = float(price)
    elif sep_diff == 1:
        if len(price_dot[-1]) != 3:
            price = float(price_tag)
        else:
            price = float(price_tag)
    else:
        price = price_tag.replace(",", ".")
        price = float(price)
    return price
slide_tags(prop, slide_size=2)
def clean_prices(price_tag):
    if pd.isna(price_tag):
        return pd.NA
    elif "$" in price_tag and "u$s" not in price_tag:
        price_tag = price_tag[1:]
        price = clean_tofloat(price_tag)
    elif "u$s" in price_tag:
        price_tag = price_tag[4:]
        price = clean_tofloat(price_tag)
        price *= 724.40 # varies through time
    elif price_tag.strip() == "tour virtual":
        price = pd.NA
    elif "uf" in price_tag:
        price_tag = price_tag[2:]
        price = clean_tofloat(price_tag)
        price *= 29302 # varies through time
    else:
        price = pd.NA
    return price
def clean_areas(area):
    if pd.isna(area):
        return pd.NA
    elif "ha" in area:
        msq = [float(value)*10000 for value in area.split() if value.isnumeric()]
        msq = msq[0] if len(msq) == 1 else msq
        return msq
    elif "tiles" in area or "totales" in area:
        msq = [float(value) for value in area.split() if value.isnumeric()]
        msq = msq[0] if len(msq) == 1 else msq
        return msq
    else:
        return pd.NA
def clean_rooms(room):
    if pd.isna(room):
        return pd.NA
    elif "dormitorio" in room:
        n_rooms = [float(value) for value in room.split() if value.isnumeric()]
        n_rooms = n_rooms[0] if len(n_rooms) == 1 else n_rooms
        return n_rooms
    else:
        return pd.NA

# Here the idea is to move every missplaced value in column "rooms",
# for this, there should be use a default location column with pd.NA value or,
# in case that the row was missing the last column, put the "rooms" value in column -3,
# becuase that column will be empty aferter the first pre-process's step.
not_rooms_mask = ["dormitorio" not in str(room) for room in prop["rooms"]]
wrong = prop.loc[prop.index[not_rooms_mask].union(pd.Index([24867,32573]))] # rows that has values not permitted in 'rooms' column
for spare_column in range(3,7):
    spare_column_mask = wrong.iloc[:,spare_column].isna()
    spare_column_index = spare_column_mask.index
    prop.iloc[spare_column_index,spare_column] = prop.loc[spare_column_index,"rooms"]
    prop.loc[spare_column_index,"rooms"] = pd.NA

#numeric_mask = [not str(room).split()[0].isnumeric() and not pd.isna(room) for room in prop["rooms"]]
#print(np.array(numeric_mask).sum())
#print(prop.loc[prop.index[numeric_mask],"rooms"])
#outliers found: 24867, 32573
not_sqm_area = ["m²" not in area and "tiles" not in area and "totales" not in area and " ha " not in area for area in prop["area"]]
goes_in_rooms_mask = ["dormitorio" in area for area in prop[not_sqm_area].loc[:,"area"]]
ngir = prop.loc[prop[not_sqm_area].index[goes_in_rooms_mask], "area"]
space_left_mask = prop.loc[ngir.index,"rooms"].isna()
prop.loc[prop.index[space_left_mask.index], "rooms"] = prop.loc[prop.index[space_left_mask.index], "area"]
prop.loc[prop.index[space_left_mask.index], "area"] = pd.NA
anywhere_mask = [~in_room for in_room in goes_in_rooms_mask]
anywhere_index = prop[not_sqm_area].index[anywhere_mask]
anyw = prop.loc[anywhere_index,:]
for spare_column in range(3,7):
    spare_column_mask = anyw.iloc[:,spare_column].isna()
    spare_column_index = spare_column_mask.index
    prop.iloc[spare_column_index, spare_column] = prop.loc[spare_column_index, "area"]
    prop.loc[spare_column_index,"area"] = pd.NA

print(prop.isna().sum())

# Cleainig direct values of different columns
prop.loc[:,"price"] = prop.loc[:,"price"].apply(lambda x: clean_prices(x))\
    #.astype(np.float32)
prop.loc[:,"area"] = prop.loc[:,"area"].apply(lambda x: clean_areas(x))\
    #.astype(np.float32)
prop['rooms'] = prop['rooms'].apply(lambda x: clean_rooms(x))
prop.iloc[:,3:7] = prop.iloc[:,3:7].astype(str).applymap(lambda x: x.lower().strip())


def check_for_odd_type():
    for i, value in enumerate(prop.iloc[:,0]):
        if isinstance(value, str):
            print(f"{value} is of type {type(value)} at index {i}")
        else:
            if i%10==0:
                print(f"index {i}, with value {value}")
#check_for_odd_type()

#prop = prop.sort_values(by='price', axis=0)
#mask = prop.iloc[:,1] > 1000
#prop = prop.drop(index=prop.index[mask])
#prop = prop.reset_index(drop=True)

prop.iloc[:,3] = prop.iloc[:,3:].apply(lambda x: ' '.join([str(c).lower().strip() for c in x]), axis=1)
prop = prop.drop(columns=[4,5], axis=0)

comm_df = pd.read_csv("Data/communes_of_chile.csv")
#comm_df = comm_df.drop(comm_df.columns[2], axis=1)
#comm_df.to_csv("Data/communes_of_chile.csv", index=False)
#print(sorted(comm_df["comuna"].unique()))
def lil_cleaning(value):
    if value == "":
        return pd.NA
    aux = [" "+val.strip()+" " for val in value.split(",")]
    if len(aux) == 1:
        return aux[0].strip()
    while True:
        for value in aux:
            mask = map(lambda x: value in x, aux)
            if sum(mask) > 1:
                aux = [val for val in aux if val != value]
                break
        else:
            break
    aux = ", ".join([val.strip() for val in aux])
    return aux
last_column = pd.Series([])
def selected_values(value, last_index, df):
    for cpr in cpr_values:
        if cpr in value:
            pass
    new_value = ", ".join()

    return new_value
for index, column in comm_df[["región", "comuna"]].iteritems():
    cpr_values = column.unique()
    #hasdata_masks = [prop["location"].apply(lambda value: comm_values in value) for comm_values in comm_values]
    #print(f"Column {index}:\n", [df.sum() for df in hasdata_masks])
    if not last_column.empty:

    prop[index] = prop["location"].apply(selected_values)
    #prop.loc[:,index] = prop.loc[:,index].apply(lambda value: value if value != "" else pd.NA)
    prop.loc[:, index] = prop.loc[:, index].apply(lambda value: lil_cleaning(value))

print(prop.iloc[:,-2:])
print(prop.iloc[:,-1].isna().sum())

mask_index = prop['location'] == 'peñalolén'
ax = prop[mask_index].plot(y='price', legend=False, kind='line')
ax2 = ax.twinx()
prop[mask_index].plot(y='m^2', ax=ax2, legend=False, kind='line', color="r")
ax.grid(True)
ax.figure.legend()
plt.show()

cat_comunas = {comuna: i for i, comuna in enumerate(prop['location'].unique())}
prop['location'] = prop['location'].apply(lambda x: cat_comunas[x])
seaborn.heatmap(prop.corr())
plt.show()