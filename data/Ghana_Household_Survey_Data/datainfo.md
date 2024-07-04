# Ghana Household Survey Data

## Description
This dataset contains detailed information from a household survey conducted in Ghana. It includes various demographic, economic, and geographic variables collected from households across different regions of the country. The data spans from 2012 to 2022 and covers aspects such as household composition, education, assets, expenditures, and food security.

## Structure
The dataset comprises the following columns with their potential values:

- `hhseriel`: Household serial number (int64)
- `hhweight`: Household weight (float64)
- `survey_year`: Year of the survey (int64) [2012, 2022]
- `country_name`: Country name (object) ["ghana"]
- `country_iso`: Country ISO code (object) ["gha"]
- `region`: Region of the household (object) ["northern", "savannah", "upper west", "bono east", "north east", "upper east"]
- `district`: District of the household (object) [17 unique values]
- `community`: Community code (object)
- `ea_code`: Enumeration area code (int64)
- `rural`: Rural or urban classification (object) ["no", "yes"]
- `religion`: Religion of the household head (object) [9 unique values]
- `hhhead_female`: Whether the household head is female (object) ["yes", "no"]
- `hhhead_marital`: Marital status of the household head (object) [7 unique values]
- `hhhmariat_redefined`: Marital status redefined (object) [3 unique values]
- `hhhead_education`: Education level of the household head (object) [16 unique values]
- `hhh_education_redefined`: Education level redefined (object) [4 unique values]
- `hhhead_literate`: Literacy status of the household head (object) [7 unique values]
- `males`: Number of males in the household (int64) [15 unique values]
- `memb_total`: Total number of household members (int64)
- `memb_und6`: Number of members under 6 years old (int64) [9 unique values]
- `memb_males_und16`: Number of males under 16 years old (int64) [11 unique values]
- `memb_und15`: Number of members under 15 years old (int64) [16 unique values]
- `memb_15_44`: Number of members aged 15-44 (int64) [15 unique values]
- `memb_45_65`: Number of members aged 45-65 (int64) [6 unique values]
- `memb_65plus`: Number of members aged 65 and above (int64) [6 unique values]
- `depend_young`: Dependency ratio for young members (float64)
- `depend_old`: Dependency ratio for old members (float64)
- `depend_total`: Total dependency ratio (float64)
- `house_rooms`: Number of rooms in the house (float64)
- `house_roof`: Type of roof material (object) [6 unique values]
- `house_electricity`: Access to electricity (object) ["yes", "no", null]
- `house_watersource`: Main source of water (object) [12 unique values]
- `house_watersource_redefined`: Water source redefined (object) [6 unique values]
- `house_toilet`: Type of toilet facility (object) [10 unique values]
- `hhh_toilet_access`: Access to toilet (object) ["yes", "no", null]
- `house_walls`: Type of wall material (object) [9 unique values]
- `house_floor`: Type of floor material (object) [9 unique values]
- `house_cost`: Cost of the house (float64)
- `house_owned`: Ownership status of the house (object) [6 unique values]
- `house_owned_redefined`: Ownership status redefined (object) [3 unique values]
- `land_owned_operated`: Land owned and operated (object) ["no", "yes", null]
- `land_owned_notoperated`: Land owned but not operated (object) ["no", "yes", null]
- `asset_telephone`: Ownership of a telephone (object) ["yes", "no", null]
- `asset_qty_poultry`: Quantity of poultry owned (float64)
- `asset_tractor`: Ownership of a tractor (object) ["no", "yes", null]
- `asset_cartplough`: Ownership of a cart/plough (object) ["no", "yes", null]
- `asset_fridge`: Ownership of a fridge (object) ["yes", "