# new EIA v2 API
# https://www.eia.gov/opendata/documentation.php

# yearly crude oil production by state and region
# "facets":[{"id":"duoarea","description":"DuoArea"},{"id":"product","description":"Product"},
#           {"id":"process","description":"Process"},{"id":"series","description":"Series"}]

### Imports and Setup

import eia
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns


# get custom API key on https://www.eia.gov/opendata/register.php
api_key = "xxxxxxxxx"

call_eia = requests.get("https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key=" + api_key + "&facets[product][]=EPC0&data[]=value&frequency=annual&start=2005")

# get all info of the dataset (dict of lists)
json_list_of_dicts = call_eia.json()["response"]["data"]


# convert json_data to data frame, retrieves data from the dict of lists
df = pd.DataFrame(json_list_of_dicts)





### Clean & Filter

# sort by period
df = df.sort_values(by="period", ascending=True)

# remove rows with "MBBL" - keep "MBBL/D"
df = df.loc[df["units"] == "MBBL/D"]

# drop excess columns
df = df.drop(["process",
              "process-name",
              "product",
              "product-name",
              "series"],
              axis=1)

# rename columns
df = df.rename(columns={"series-description": "state"})

# remove rows in order to sum all values to add new "total production" series (in future, make it a separate df?)
df = df.loc[(df["duoarea"] != "RAKS") &
            (df["duoarea"] != "R10") &
            (df["duoarea"] != "R5F") &
            (df["duoarea"] != "R30") &
            (df["duoarea"] != "R20") &
            (df["duoarea"] != "R40") &
            (df["duoarea"] != "R50")]

# remove excess string
df['state'] = df['state'].str[:-57]

# shorten GoM
df['state'] = df['state'].str.replace("Federal Offshore--", "")





### Visuals + Analysis

sns.set_theme(style="darkgrid")


## plot1: Total US Production
# Visual1
df_total_prod = df.groupby("period").sum()

df_plot1 = df_total_prod.reset_index()
ax = sns.barplot(data=df_plot1, x="period", y="value")
ax.set(xlabel="year", ylabel="production (mbbl/d)", title="Total U.S. Crude Oil Production")
plt.xticks(rotation=45)
plt.show()


# Analysis1
period_latest = df_plot1["period"].max()
value_latest = df_plot1.loc[df_plot1["period"] == period_latest]["value"].item()
value_2005 = df_plot1.loc[df_plot1["period"] == 2005]["value"].item()
amt_inc_dec = value_latest - value_2005
pct_inc_dec = "{:.0%}".format(value_latest / value_2005 - 1)

print("\n--------------- Analysis ---------------")
print("Total U.S. crude oil production was " + str(value_latest) + " thousand barrels per day in " + period_latest.astype('str'))
print("This is a " + str(amt_inc_dec) + " thousand barrel per day" + (" increase" if amt_inc_dec >=0 else " decrease)") + " vs. 2005, or " + ("+" if amt_inc_dec >=0 else "-") + str(pct_inc_dec))





## plot2: Texas production
# Visual2
df_plot2 = df[df["state"] == "Texas"]
ax = sns.lineplot(data=df_plot2, x="period", y="value")
plt.xticks(rotation=45)
plt.show()


# Analysis2
period_latest = df_plot2["period"].max()
value_latest = df_plot2.loc[df_plot2["period"] == period_latest]["value"].item()
value_2005 = df_plot2.loc[df_plot2["period"] == 2005]["value"].item()
amt_inc_dec = value_latest - value_2005
pct_inc_dec = "{:.0%}".format(value_latest / value_2005 - 1)

print("\n--------------- Analysis ---------------")
print("Total Texas crude oil production was " + str(value_latest) + " thousand barrels per day in " + period_latest.astype('str'))
print("This is a " + str(amt_inc_dec) + " thousand barrel per day" + (" increase" if amt_inc_dec >=0 else " decrease)") + " vs. 2005, or " + ("+" if amt_inc_dec >=0 else "-") + str(pct_inc_dec))

# (FUTURE ENHANCEMENT: display any state's production chart + analysis through user input)





## plot3: Top 10 crude oil producing states, latest period
# Visual3
df_state_latest_prod = df[df["period"] == df["period"].max()].sort_values(by="value", ascending=False)
df_state_latest_prod_top10 = df_state_latest_prod[0:10]

df_plot3 = df_state_latest_prod_top10
ax = sns.barplot(data=df_plot3, x="state", y="value")
ax.set(xlabel="state", ylabel="production (mbbl/d)", title="Top 10 Crude Oil Producing States - " + str(df["period"].max()))
plt.xticks(rotation=45, ha="right")
plt.show()


# Analysis3
print("\n--------------- Analysis ---------------\n")
print("The top 10 crude oil producing states in " + str(df["period"].max()) + " and their production levels were: ")
for ind in df_plot3.index:
    print("{0:20}{1:5d}".format(df_plot3["state"][ind], df_plot3["value"][ind]) + " mbbl/d")





# plot4: Top 10 crude oil producing states in 2021, % of total
df_total_2021_prod = df_total_prod.loc[2021]["value"]

df_state_2021_prod_filtered["% of total"] = df_state_2021_prod_filtered["value"].div(df_total_2021_prod)

df_plot4 = df_state_2021_prod_filtered
ax = sns.barplot(data=df_plot4, x="state", y="% of total")
ax.set(xlabel="state", ylabel="% of total", title="Top 10 Crude Oil Production States - 2021")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
plt.xticks(rotation=45, ha="right")
plt.show()





# plot5: % share of total US production since 2005, top 5 states
df_indexed = df.set_index(["period", "duoarea", "area-name", "state", "units"])
df_pct_of_total = (df_indexed/ df_total_prod).reset_index()

top_5_producers = df_state_2021_prod[0:5]["state"].unique()

df_plot5 = df_pct_of_total[df_pct_of_total["state"].isin(top_5_producers)].sort_values(by=["period", "value"], ascending=[False, False])
ax = sns.lineplot(data=df_plot5, x="period", y="value", hue="state")
ax.set(xlabel="", ylabel="% of total", title="Top 5 States' % of Total US Crude Production")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
plt.xticks(np.arange(min(df_plot5["period"]), max(df_plot5["period"])+1, 1.0), rotation=45, ha="right")
plt.yticks(np.arange(0, max(df_plot5["value"])+0.1, 0.1))
plt.show()
