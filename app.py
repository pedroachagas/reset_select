import streamlit as st
import numpy as np

SALADA = 130
CALORIES_PER_G_PROTEIN = 4
CALORIES_PER_G_CARBOHYDRATE = 4
CALORIES_PER_G_FAT = 9
RATIO_CARBOHYDRATE = 0.5
RATIO_FAT = 0.3
PROTEIN_PER_KG = 2.2


def calculate_protein(weight):
    kcal_protein = weight * PROTEIN_PER_KG * CALORIES_PER_G_PROTEIN
    groups_protein = kcal_protein / 105

    if weight < 65:
        if groups_protein < 6:
            groups_protein = 6
    if 65 <= weight < 75:
        if groups_protein < 7:
            groups_protein = 7
    if 75 <= weight < 85:
        if groups_protein < 9:
            groups_protein = 9
    if weight >= 85:
        if groups_protein < 10:
            groups_protein = 10

    return groups_protein

def calculate_kcals_groups(calories, weight, carb_fat_percent, ratio_carb, ratio_fat):
    groups_protein = calculate_protein(weight)
    kcals_protein = groups_protein * 105
    kcals_carb = (calories - kcals_protein - SALADA) * carb_fat_percent
    kcals_fat = (calories - kcals_protein - SALADA) * (1 - carb_fat_percent)

    return kcals_protein, kcals_carb, kcals_fat

def distribute_groups(kcals_protein, kcals_carb, kcals_fat, ratio_carb, ratio_fat):
    portion_sizes = {
        4: ('protein', (105, 15)),
        5: ('carb', (32, 7)),
        11: ('fat', (115, 9.8)),
        12: ('carb', (75, 15)),
        13: ('fat', (97, 10.7))
    }

    groups = {
        4: kcals_protein / portion_sizes[4][1][0],
        5: kcals_carb * (1 - ratio_carb) / portion_sizes[5][1][0],
        12: kcals_carb * ratio_carb / portion_sizes[12][1][0],
        11: kcals_fat * (1 - ratio_fat) / portion_sizes[11][1][0],
        13: kcals_fat * ratio_fat / portion_sizes[13][1][0]
    }

    return groups

def check_calories(portions_dict):
    portion_sizes = {
        4: ('protein', (105, 15)),
        5: ('carb', (32, 7)),
        11: ('fat', (115, 9.8)),
        12: ('carb', (75, 15)),
        13: ('fat', (97, 10.7))
    }

    total_calories = 0
    for group_id, num_portions in portions_dict.items():
        _, (calories_per_portion, _) = portion_sizes[group_id]
        total_calories += num_portions * calories_per_portion

    return (total_calories)

def round_portions(portions_dict):
    for key in portions_dict:
        portions_dict[key] = int(np.round(portions_dict[key]))

    return dict(sorted(portions_dict.items()))

def main():
    st.title("Daily Macro-Nutrient Calculator")

    calories = st.number_input("Total Daily Calories", value=2000)
    weight = st.number_input("Weight (kg)", value=70)

    carb_fat_percent = st.slider("Gord vs Carb", 0.0, 1.0, 0.5)
    ratio_carb = st.slider("Grupo 5 vs 12", 0.0, 1.0, 0.5)
    ratio_fat = st.slider("Grupo 11 vs 13", 0.0, 1.0, 0.5)

    if st.button("Calculate"):

        kcals_protein, kcals_carb, kcals_fat = calculate_kcals_groups(calories, weight, carb_fat_percent, ratio_carb, ratio_fat)
        portions_dict = distribute_groups(kcals_protein, kcals_carb, kcals_fat, ratio_carb, ratio_fat)

        portions_dict = round_portions(portions_dict)

        total_calories = check_calories(portions_dict)

        st.write("## Recommended Portions")
        st.metric("Total Calories", total_calories + SALADA, delta=None)

        columns = st.columns(5)
        for idx, (group_id, num_portions) in enumerate(portions_dict.items()):
            columns[idx].metric(label=f"Group {group_id}", value=num_portions)



if __name__ == "__main__":
    main()

