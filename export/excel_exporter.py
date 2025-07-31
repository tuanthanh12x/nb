import pandas as pd

def export_to_excel(data):
    df = pd.DataFrame(data, columns=["ID", "Username"])
    df.to_excel("exported_users.xlsx", index=False)
    print("Excel exported.")
