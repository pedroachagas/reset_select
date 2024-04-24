import streamlit as st
import numpy as np

SALADA = 130
CALORIES_PER_G_PROTEIN = 4
PROTEIN_PER_KG = 2.2
KCALS_G4 = 105
KCALS_G5 = 32
KCALS_G11 = 115
KCALS_G12 = 75
KCALS_G13 = 97
PROT_65 = 6
PROT_65_75 = 7
PROT_75_85 = 9
PROT_85 = 10

def calculate_protein(weight):
    kcal_protein = weight * PROTEIN_PER_KG * CALORIES_PER_G_PROTEIN
    groups_protein = kcal_protein / KCALS_G4

    if weight < 65:
        groups_protein = max(groups_protein, PROT_65)
    elif 65 <= weight < 75:
        groups_protein = max(groups_protein, PROT_65_75)
    elif 75 <= weight < 85:
        groups_protein = max(groups_protein, PROT_75_85)
    elif weight >= 85:
        groups_protein = max(groups_protein, PROT_85)

    return groups_protein

def calculate_kcals_groups(calories, weight, carb_fat_percent, ratio_carb, ratio_fat):
    groups_protein = calculate_protein(weight)
    kcals_protein = groups_protein * KCALS_G4
    remaining_calories = calories - kcals_protein - SALADA

    kcals_gord = remaining_calories * (1 - carb_fat_percent)
    kcals_carb = remaining_calories * carb_fat_percent

    return {
        4: kcals_protein,
        5: kcals_carb * (1 - ratio_carb),
        12: kcals_carb * ratio_carb,
        11: kcals_gord * (1 - ratio_fat),
        13: kcals_gord * ratio_fat
    }

def calculate_portions(kcals_dict):
    portion_sizes = {
        4: KCALS_G4,
        5: KCALS_G5,
        11: KCALS_G11,
        12: KCALS_G12,
        13: KCALS_G13
    }

    return round_portions({
        group_id: kcals / portion_sizes[group_id]
        for group_id, kcals in kcals_dict.items()
    })

def check_calories(portions_dict):
    portion_sizes = {
        4: KCALS_G4,
        5: KCALS_G5,
        11: KCALS_G11,
        12: KCALS_G12,
        13: KCALS_G13
    }

    total_calories = 0
    for group_id, num_portions in portions_dict.items():
        calories_per_portion = portion_sizes[group_id]
        total_calories += num_portions * calories_per_portion

    return total_calories + SALADA

def round_portions(portions_dict):
    for key in portions_dict:
        portions_dict[key] = int(np.round(portions_dict[key]))

    return dict(sorted(portions_dict.items()))


def main():
    st.title("Calculadora de Porções de Grupos Alimentares")
    st.subheader("RESET METHOD SELECT")

    with st.form(key='inputs_form'):
        calories = st.number_input("Gasto Energético Total (kcals)", value=1500)
        weight = st.number_input("Peso (kg)", value=60)
        carb_fat_percent = st.slider("Gord vs Carb", 0.0, 1.0, 0.5)
        ratio_carb = st.slider("Grupo 5 vs 12", 0.0, 1.0, 0.5)
        ratio_fat = st.slider("Grupo 11 vs 13", 0.0, 1.0, 0.5)
        submit_button = st.form_submit_button(label='Calculate')

    if submit_button:
        kcals_dict = calculate_kcals_groups(calories, weight, carb_fat_percent, ratio_carb, ratio_fat)
        portions_dict = calculate_portions(kcals_dict)
        st.session_state['portions_dict'] = portions_dict

    if 'portions_dict' in st.session_state:
        st.write("## Distribuição sugerida de porções")
        col_groups = st.columns(5)
        for idx, (group_id, num_portions) in enumerate(st.session_state['portions_dict'].items()):
            col_groups[idx].metric(label=f"Grupo {group_id}", value=num_portions)

        st.write("## Validação de porções")
        with st.form(key='validation_form'):
            custom_portions_dict = {}
            col_inputs = st.columns(5)
            for i, group_id in enumerate([4, 5, 11, 12, 13]):
                custom_portions_dict[group_id] = col_inputs[i].number_input(f"Grupo {group_id}", value=st.session_state.portions_dict[group_id])
            validate_button = st.form_submit_button(label='Validate Portions')

            if validate_button:
                total_calories = check_calories(custom_portions_dict)
                st.metric("Total Calories", total_calories)

if __name__ == "__main__":
    main()

