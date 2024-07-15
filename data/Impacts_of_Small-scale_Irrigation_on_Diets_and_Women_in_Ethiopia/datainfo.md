```markdown
# Title: Impacts of Small-scale Irrigation on Diets and Women in Ethiopia

## Description:
This dataset explores the impacts of small-scale irrigation on the diets and socio-economic status of women in Ethiopia. It includes various demographic, socio-economic, and agricultural variables collected from households and individuals. The data aims to provide insights into how small-scale irrigation affects dietary diversity, women's autonomy, and overall household welfare.

## Structure:
The dataset contains the following columns with their potential values:

- **hhid**: Household ID (unique identifier)
- **mid**: Member ID (1, 2, 3, 4, 5, 6, 8)
- **sex**: Gender of the respondent (male, female)
- **hh_type**: Household type (yes, both male(s) and female(s), yes, has female(s) only)
- **autonomy_inc**: Autonomy in income (0, 1)
- **selfeff**: Self-efficacy (0.0, 1.0, null)
- **never_violence**: Never experienced violence (0.0, 1.0, null)
- **respect**: Respect (0.0, 1.0, null)
- **feelinputdecagr**: Feels input in decision-making in agriculture (0.0, 1.0, null)
- **credit_accdec**: Access to credit decision (0.0, 1.0, null)
- **incomecontrol**: Control over income (0.0, 1.0, null)
- **work_balance**: Work-life balance (0.0, 1.0, null)
- **mobility**: Mobility (0.0, 1.0, null)
- **groupmember**: Group membership (0.0, 1.0, null)
- **group_inf**: Influence in group (0.0, 1.0, null)
- **cont_inputprod**: Contribution to input production (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, null)
- **cont_assets**: Contribution to assets (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, null)
- **cont_credit**: Contribution to credit (0, 1, 2, 3, 4)
- **cont_income**: Contribution to income (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, null)
- **cont_group**: Contribution to group (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, null)
- **cont_group_inf**: Contribution to group influence (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, null)
- **cont_workload**: Contribution to workload (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, null)
- **cont_mobility**: Contribution to mobility (0, 1, 2, 3, 4, 5)
- **cont_respect**: Contribution to respect (0.0, 1.0, 2.0, 3.0, 4.0, null)
- **cont_violence**: Contribution to violence (0.0, null)
- **cont_selfeff**: Contribution to self-efficacy (4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, null)
- **indid**: Individual ID (unique identifier)
- **kebele**: Kebele (1, 2, 3, 4, 5, 6, 98)
- **woreda**: Woreda (1, 2)
- **village**: Village (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98)
- **g103**: General question 103 (yes, no)
- **g104**: General question 104 (null, refused)
- **g102replace**: General question 102 replace (null)
- **g102**: General question 102 (1, 2, 3, 4, 5, 6, 8)
- **resp_gender**: Respondent gender (1, 2)
- **g106**: General question 106 (with adults of both sexes, with adult males, with adult females, with both adults and child/children, with child/children, alone, null)
- **a01**: Activity 01 (1, 2, 3, 4, 5, 6, 8)
- **a02**: Activity 02 (primary respondent, mother/father, spouse, son/daughter, grandson/granddaughter, brother/sister, son/daughter-in-law)
- **a04**: Age (18 to 92)
- **a05**: Marital status (never married, currently married, widow/widower, divorcee, separated/deserted)
- **a06**: Occupation (crop production, self-employed, student, other, non-agricultural wage worker, jobless, agricultural wage worker)
- **a06othr**: Other occupation (null, tireta, selling local beverage, fisher man, pension salary, merchant)
- **a08**: Activity 08 (yes, no)
- **g2_02_id1_a**: General question 2_02 ID1 A (1.0, 2.0, null, 94.0, 98.0, 6.0, 4.0, 3.0, 7.0, 10.0)
- **g2_02_id2_a**: General question 2_02 ID2 A (2.0, 3.0, null, 94.0, 4.0, 5.0, 10.0)
- **g2_02_id3_a**: General question 2_02 ID3 A (3.0, 4.0, 5.0, 94.0, 6.0, null)
- **g3_09_a**: General question 3_09 A (null, yes, in-kind, no)
- **g3_10_a**: General question 3_10 A (null, 1 2, 2 4)
- **g3_11_a**: General question 3_11 A (null, 1 2, 2 4)
- **g3_12_a**: General question 3_12 A (null, 1 2, 2 4)
- **g3_10_id1_a**: General question 3_10 ID1 A (null, 1.0, 2.0)
- **g3_10_id2_a**: General question 3_10 ID2 A (null, 2.0, 4.0)
- **g3_10_id3_a**: General question 3_10 ID3 A (null)
- **g3_11_id1_a**: General question 3_11 ID1 A (null, 1.0, 2.0)
- **g3_11_id2_a**: General question 3_11 ID2 A (null, 2.0, 4.0)
- **g3_11_id3_a**: General question 3_11 ID3 A (null)
- **g3_12_id1_a**: General question 3_12 ID1 A (null, 1.0, 2.0)
- **g3_12_id2_a**: General question 3_12 ID2 A (null, 2.0, 4.0)
- **g3_12_id3_a**: General question 3_12 ID3 A (null)
- **g3_09_b**: General question 3_09 B (null, yes, cash, no, yes, cash and in-kind, don't know)
- **g3_10_b**: General question 3_10 B (null, 1 2, 1, 1 2 3)
- **g3_11_b**: General question 3_11 B (null, 1 2, 1, 1 2 3)
- **g3_12_b**: General question 3_12 B (null, 1, 1 2, 1 2 3)
- **g3_10_id1_b**: General question 3_10 ID1 B (null, 1.0)
- **g3_10_id2_b**: General question 3_10 ID2 B (null, 2.0)
- **g3_10_id3_b**: General question 3_10 ID3 B (null, 3.0)
- **g3_11_id1_b**: General question 3_11 ID1 B (null, 1.0)
- **g3_11_id2_b**: General question 3_11 ID2 B (null, 2.0)
- **g3_11_id3_b**: General question 3_11 ID3 B (null, 3.0)
- **g3_12_id1_b**: General question 3_12 ID1 B (null, 1.0)
- **g3_12_id2_b**: General question 3_12 ID2 B (null, 2.0)
- **g3_12_id3_b**: General question 3_12 ID3 B (null, 3.0)
- **g3_10_d**: General question 3_10 D (null, 1 2, 1, 2, 1 2 3, 1 2 4, 4, 2 3, 3, 1 3, 94)
- **g3_11_d**: General question 3_11 D (null, 1 2, 1, 1 2 3, 1 2 4, 4, 2, 2 3, 3, 1 3, 94)
- **g3_12_d**: General question 3_12 D (null, 1 2, 2, 1, 1 2 3, 1 2 4, 4, 2 3, 3, 1 3, 94)
- **g3_10_id1_d**: General question 3_10 ID1 D (null, 1.0, 2.0, 4.0, 3.0, 94.0)
- **g3_10_id2_d**: General question 3_10 ID2 D (null, 2.0, 3.0)
- **g3_10_id3_d**: General question 3_10 ID3 D (null, 3.0, 4.0)
- **g3_11_id1_d**: General question 3_11 ID1 D (null, 1.0, 4.0, 2.0, 3.0, 94.0)
- **g3_11_id2_d**: General question 3_11 ID2 D (null, 2.0, 3.0)
- **g3_11_id3_d**: General question 3_11 ID3 D (null, 3.0, 4.0)
- **g3_12_id1_d**: General question 3_12 ID1 D (null, 1.0, 2.0, 4.0, 3.0, 94.0)
- **g3_12_id2_d**: General question 3_12 ID2 D (null, 2.0, 3.0)
- **g3_12_id3_d**: General question 3_12 ID3 D (null, 3.0, 4.0)
- **s3p2**: S3P2 (0.0 to 180.0)
- **s3p3**: S3P3 (cropped, borrowed out, virgin, pasture, fallow, rented out, null, other, woodlot)
- **s3p5**: S3P5 (1995 to 2015)
- **s3p6**: S3P6 (yes, null, no)
- **s3p7**: S3P7 (1995 to 2015)
- **s3p10**: S3P10 (no, yes, null)
- **landsize**: Land size (1.0 to 115.0)
- **unit**: Unit (kada, timad, hectares, null, other, square meters)
- **s3_hirela**: S3 Hire LA (20.0 to 2000.0)
- **s3_hirelb**: S3 Hire LB (50.0 to 977.0)
- **s3_hirelc**: S3 Hire LC (50.0 to 997.0)
- **pweight_s**: PWeight S (1)

## Context:
The dataset was collected to understand the socio-economic and dietary impacts of small-scale irrigation projects in Ethiopia. It includes information on household composition, gender roles, economic activities, and agricultural practices. The data provides valuable insights into how irrigation influences food security, women's empowerment, and household welfare.

## Usage Notes:
### Limitations:
- The dataset may contain missing values and null entries.
- Some variables have a limited range of potential values, which may affect the granularity of the analysis.

### License:
Data is licensed under the Creative Commons Attribution 4.0 International License.

## Technical Information:
### Format:
- CSV (.csv)
```