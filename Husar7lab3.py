#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 21:11:42 2022

@author: Kat
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt



st.title("Kat Husar Lab 3: Ethics in Data Visualization")

st.header("Set Up")

st.markdown("In this lab, we will look at the subset of climate dataset.\
            We first remove any countries that have 80% or more of missing data. \
                Then we focus on 5 countries with the highest emission levels in 2019. \
                    In particular, the data from years 2010 to 2019.")




link = 'https://raw.githubusercontent.com/KatHusar/CSE5544_Lab3/main/ClimateData.csv'
df_data = pd.read_csv(link)

col = df_data.columns
col =col.rename(None)

df_data.loc[:, :].replace(['..'],[np.nan],inplace=True)
#change object type
df_data[col[2:]] = df_data[col[2:]].apply(pd.to_numeric,  errors='coerce')

remove = []
#find rows with a lot of missing data
for i in range(df_data.shape[0]):
  if sum(df_data.iloc[i].isnull().values.ravel()) > 24:
    remove.append(i)


filtered_data = df_data.copy()
rows = filtered_data.index[remove]
filtered_data.drop(rows, inplace=True)
#remove Total
filtered_data = filtered_data.loc[filtered_data['Country\year'] != 'OECD - Total']
filtered_data = filtered_data[filtered_data['Country\\year'].apply(lambda x: 'OECD' not in x and 'European Union' not in x)]

# only top 5 countries

df_top5 = filtered_data.sort_values(by=['2019'],  ascending=False)
df_top5= df_top5[df_top5['Country\\year'].apply(lambda x: 'OECD' not in x and 'European Union' not in x)].head(5)
data5 = df_top5.drop(columns=['Non-OECD Economies'])
data5 = pd.melt(data5, id_vars=['Country\year'], var_name='year')

df5 = df_top5[['Country\\year', '2010' , '2011','2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']]
df5 = df5.reset_index(drop=True)

# outside data
pop = [328.3, 144.4, 126.3, 83.09, 37.59] # World Bank
area = [3.797, 6.612, 0.146, 0.138, 3.855] # Wikipedia
coeff = np.multiply(pop,area)

# rescale the data so that we look at emissions per mil sq mi per mil people
# larger countries and more populated areas are expected to have higher total emission
# we acconunt for that by dividing by area of the country and its population

df5_scaled = pd.DataFrame.copy(df5)
for i in range(5):
  df5_scaled.loc[i:i, [ '2010' , '2011','2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']] = np.round(df5.loc[i:i,[ '2010' , '2011','2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']]/coeff[i],2)

# Prep data for plots
df5_m =  pd.melt(df5, id_vars=['Country\year'], var_name='year')
df5_scaled_m = pd.melt(df5_scaled, id_vars=['Country\year'], var_name='year')

df5_m.rename(columns={'Country\year':'country'}, inplace=True)
df5_scaled_m.rename(columns={'Country\year':'country'}, inplace=True)


st.header("Visualization")

st.subheader("Dishonest/Unethical/Deceiving Perspective")

st.markdown("Heatmap of emmision levels of the five countries in the years 2010-2019.")
# heatmap using altair
heatmap = alt.Chart(df5_m, title=['Stop the US!','', 'Emission levels THREE times higher']).mark_rect().encode(
    x = alt.X('country:N'),
    y = alt.Y('year:O'),
    color = alt.Color('value:Q', scale=alt.Scale( type = 'log', scheme='rainbow', reverse = True, nice=True))
).properties(
    width=800,
    height=300).configure_title(fontSize=20)
    
    

st.altair_chart(heatmap, use_container_width = True)

st.subheader("Honest/Ethical/Truthful Perspective")

st.markdown("Countries with larger areas will often have higher emission levels.\
            It does not make sense to compare  countrie like the United States and Italy due to large area discreptacy.\
                Similarly, highly populated countries can be expected to have higher total emission levels.\
                    Therefore, we rescale our data by calculating emissions per million square miles per million people.\
                        This number will have a better representation of emission levels adjusted to area and population.")
                        
# heatmap


rect = alt.Chart(df5_scaled_m, title=["Emissions per population and area",'2010-2019','']).mark_rect().encode(
    alt.X('country:N', title = 'Country', axis=alt.Axis(
                                   labelAngle=-45)),
    alt.Y('year:O', title = 'Year'),
    alt.Color('value:Q',scale=alt.Scale( type = 'sqrt', scheme='inferno', nice=True),
        legend=alt.Legend(title=['Emission (tons of CO2)', 'per million people', ' per milion sq mi','']))).properties(
    width=800,
    height = 400)
text = rect.mark_text(baseline='middle').encode(
    text='value:Q',
    color=alt.condition(
        alt.datum.value > 6000,
        alt.value('black'),
        alt.value('white')
    )
)
heatmap2 = (rect+text).configure_axis(
    labelFontSize=12,
    titleFontSize=15).configure_title(fontSize=24)
st.altair_chart(heatmap2, use_container_width = True)

st.header("Conclusion")

st.markdown("In the first plot, even though the colors can be somewhat ordered, it is difficult to see how the differences of colors represent\
            the difference in actual emission values. In title of the plot, it is suggested that the United States cause the most problen due to high levels of emission.\
                Howeve, since the country is compared directly to other countries rather than regions of similar area and population, it created deceitful understanding.\
                    Additionaly, the legend does not explain what \'value\' means and what units are used. The second plot is a lot easier to follow as in addition to the color, \
                        the numbers are added to show exact values. The legend specifies units, and the square root transformation of color map shows us better \
                            the difference in emission levels in the same country between different years. ")