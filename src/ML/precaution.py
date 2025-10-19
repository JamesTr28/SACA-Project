import pandas as pd

def get_precaution(disease: str):
    df = pd.read_csv("hf://datasets/shanover/disease_symptoms_prec_full/disease_sympts_prec_full.csv")
    result = df.loc[df['disease'].str.lower() == disease.lower(), 'precautions']
    if not result.empty:
        precautions = [p.strip() for p in result.values[0].split(',')]
    else:
        precautions = []

    print(precautions)
    return precautions

if __name__ == "__main__":
    get_precaution("Fungal Infection")