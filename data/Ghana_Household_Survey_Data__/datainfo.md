**

```markdown
# Title: Ghana Household Survey Data

## Description:
The Ghana Household Survey Data is a comprehensive dataset that captures various socio-economic and demographic attributes of households in Ghana. The dataset includes information on household characteristics, education, health, assets, expenditures, and access to services, among other variables. It is designed to provide insights into the living conditions and well-being of households in different regions of Ghana.

## Structure:
The dataset contains the following columns with their potential values:

- **hhseriel**: Unique household identifier (int64)
- **hhweight**: Household weight (float64)
- **survey_year**: Year of the survey (int64) [2012, 2022]
- **country_name**: Country name (object) ["ghana"]
- **country_iso**: Country ISO code (object) ["gha"]
- **region**: Region name (object) ["northern", "savannah", "upper west", "bono east", "north east", "upper east"]
- **district**: District name (object) [17 unique values]
- **community**: Community identifier (object)
- **ea_code**: Enumeration area code (int64)
- **rural**: Rural or urban classification (object) ["no", "yes"]
- **religion**: Religion of household head (object) [9 unique values]
- **hhhead_female**: Whether household head is female (object) ["yes", "no"]
- **hhhead_marital**: Marital status of household head (object) [7 unique values]
- **hhhmariat_redefined**: Marital status redefined (object) [3 unique values]
- **hhhead_education**: Education level of household head (object) [16 unique values]
- **hhh_education_redefined**: Education level redefined (object) [4 unique values]
- **hhhead_literate**: Literacy status of household head (object) [7 unique values]
- **males**: Number of males in household (int64) [15 unique values]
- **memb_total**: Total number of household members (int64)
- **memb_und6**: Number of household members under 6 years (int64)
- **memb_males_und16**: Number of male household members under 16 years (int64)
- **memb_und15**: Number of household members under 15 years (int64)
- **memb_15_44**: Number of household members aged 15-44 years (int64)
- **memb_45_65**: Number of household members aged 45-65 years (int64)
- **memb_65plus**: Number of household members aged 65 years and above (int64)
- **depend_young**: Dependency ratio for young members (float64)
- **depend_old**: Dependency ratio for old members (float64)
- **depend_total**: Total dependency ratio (float64)
- **house_rooms**: Number of rooms in the house (float64)
- **house_roof**: Type of roofing material (object) [6 unique values]
- **house_electricity**: Access to electricity (object) ["yes", "no", null]
- **house_watersource**: Main source of water (object) [12 unique values]
- **house_watersource_redefined**: Water source redefined (object) [6 unique values]
- **house_toilet**: Type of toilet facility (object) [10 unique values]
- **hhh_toilet_access**: Access to toilet (object) ["yes", "no", null]
- **house_walls**: Type of wall material (object) [9 unique values]
- **house_floor**: Type of floor material (object) [9 unique values]
- **house_cost**: Cost of the house (float64)
- **house_owned**: Ownership status of the house (object) [6 unique values]
- **house_owned_redefined**: House ownership redefined (object) [3 unique values]
- **land_owned_operated**: Land ownership and operation status (object) ["no", "yes", null]
- **land_owned_notoperated**: Land ownership but not operated (object) ["no", "yes", null]
- **asset_telephone**: Ownership of a telephone (object) ["yes", "no", null]
- **asset_qty_poultry**: Quantity of poultry owned (float64)
- **asset_tractor**: Ownership of a tractor (object) ["no", "yes", null]
- **asset_cartplough**: Ownership of a cart/plough (object) ["