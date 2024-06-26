import streamlit as st
import numpy as np

SALADA = 100
CALORIES_PER_G_PROTEIN = 4
PROTEIN_PER_KG = 2.2

WEIGHT_PROTEIN_REQUIREMENTS = {
    65: 6,
    75: 7,
    85: 9,
    float('inf'): 10
}

GROUP_CALORIES = {
    4: 105,
    5: 32,
    11: 115,
    12: 75,
    13: 97
}

def calculate_protein(weight):
    kcal_protein = weight * PROTEIN_PER_KG * CALORIES_PER_G_PROTEIN
    groups_protein = kcal_protein / GROUP_CALORIES[4]

    for weight_threshold, min_protein in WEIGHT_PROTEIN_REQUIREMENTS.items():
        if weight < weight_threshold:
            return max(groups_protein, min_protein)

def calculate_kcals_groups(calories, weight, carb_fat_percent, ratio_carb, ratio_fat):
    groups_protein = calculate_protein(weight)
    kcals_protein = groups_protein * GROUP_CALORIES[4]
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

    return round_portions({
        group_id: kcals / GROUP_CALORIES[group_id]
        for group_id, kcals in kcals_dict.items()
    })

def check_calories(portions_dict):

    total_calories = 0
    for group_id, num_portions in portions_dict.items():
        calories_per_portion = GROUP_CALORIES[group_id]
        total_calories += num_portions * calories_per_portion

    return int(total_calories + SALADA)

def round_portions(portions_dict):
    for key in portions_dict:
        portions_dict[key] = int(np.round(portions_dict[key]))

    return dict(sorted(portions_dict.items()))

def main():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(' ')
    with col2:
        st.image("imgs/ResetM30_17.png", width=200)
    with col3:
        st.write(' ')

    st.title("Calculadora de Porções")
    st.subheader("RESET METHOD SELECT")

    with st.form(key='inputs_form'):
        calories = st.number_input("Gasto Energético Total (kcals)", value=1500)
        weight = st.number_input("Peso (kg)", value=60)
        carb_fat_percent = st.slider("Gord vs Carb", 0.0, 1.0, 0.5)
        ratio_carb = st.slider("Grupo 5 vs 12", 0.0, 1.0, 0.5)
        ratio_fat = st.slider("Grupo 11 vs 13", 0.0, 1.0, 0.5)
        submit_button = st.form_submit_button(label='Gerar distribuição de porções')

    if submit_button:
        kcals_dict = calculate_kcals_groups(calories, weight, carb_fat_percent, ratio_carb, ratio_fat)
        portions_dict = calculate_portions(kcals_dict)
        st.session_state['portions_dict'] = portions_dict

    if 'portions_dict' in st.session_state:
        st.write("## Distribuição sugerida de porções")
        col_groups = st.columns(5)
        for idx, (group_id, num_portions) in enumerate(st.session_state['portions_dict'].items()):
            col_groups[idx].metric(label=f"Grupo {group_id}", value=num_portions)

        st.write("## Validação de distribuição de porções")
        with st.form(key='validation_form'):
            custom_portions_dict = {}
            col_inputs = st.columns(5)
            for i, group_id in enumerate(GROUP_CALORIES.keys()):
                custom_portions_dict[group_id] = col_inputs[i].number_input(f"Grupo {group_id}", value=float(st.session_state.portions_dict[group_id]), step=1.,format='%.1f')
            validate_button = st.form_submit_button(label='Calcular calorias totais')

            if validate_button:
                st.write("Caloras por grupo")
                cols = st.columns(5)
                for i, group_id in enumerate(GROUP_CALORIES.keys()):
                    cols[i].metric(label=f"Grupo {group_id}", value=int(custom_portions_dict[group_id] * GROUP_CALORIES[group_id]))

                total_calories = check_calories(custom_portions_dict)
                cols[0].metric("Calorias de grupos", total_calories - SALADA)
                cols[1].metric("+Salada", SALADA)
                cols[2].metric("=Total", total_calories)


if __name__ == "__main__":
    main()

