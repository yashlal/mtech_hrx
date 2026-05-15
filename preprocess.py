import numpy as np
import pandas as pd

df = pd.read_csv("data/data_raw.csv")
logs = pd.read_csv("data/contact_logs_raw.csv")
coach_df = pd.read_csv("data/coach_raw.csv")

df.rename(columns={'Study arm (use this field)': 'Study arm'}, inplace=True)
df.rename(columns={'eHEALS score (range: 10-50)': 'eHEALS score'}, inplace=True)

# STEP 1 - filter patients
# keep only patients who have at least 1 "Patient Contact" row
has_contact = logs.groupby("Record ID")["Event Name"].apply(
    lambda x: (x == "Patient Contact").any()
)

# keep only patients who have a "Randomization" row with nonempty Study arm
has_randomization = df.groupby("Record ID").apply(
    lambda g: ((g["Event Name"] == "Randomization") & (g["Study arm"].notna()) & (g["Study arm"] != "")).any()
)

has_coach = coach_df.groupby("Record ID")["Event Name"].apply(
    lambda x: x.str.endswith("Coaching Call", na=False).any()
)

# FIRST, WE DO ALL THE SETUP FOR THE COACHING CALLS
df2 = df.copy()
df_valid = df2[df2["Record ID"].isin(has_coach[has_coach].index)]

df_valid = (
    df_valid
    .groupby('Record ID', as_index=False)
    .agg(lambda x: x.dropna().iloc[0] if x.notna().any() else pd.NA)
)
df_valid = df_valid.drop(['Event Name','Repeat Instrument','Repeat Instance'], axis=1)

coach_valid = coach_df[coach_df['Event Name'].str.endswith('Coaching Call', na=False)]
df_valid['Date of scheduled PFA'] = pd.to_datetime(df_valid['Date of scheduled PFA'])

final_coach_df = coach_valid.merge(
    df_valid,
    on='Record ID',
    how='left'
)

final_coach_df.rename(columns={'Age in years': 'Age',
                         'Duration of call in minutes': 'Call Duration'}, inplace=True)
final_coach_df.to_csv("data/preproc_coach.csv")

# SECOND, WE SETUP FOR THE PT CONTACT CALLS
valid_patients = has_contact & has_randomization
df3 = df.copy()

df_valid2 = df3[df3["Record ID"].isin(valid_patients[valid_patients].index)]

df_valid2 = (
    df_valid2
    .groupby('Record ID', as_index=False)
    .agg(lambda x: x.dropna().iloc[0] if x.notna().any() else pd.NA)
)
df_valid2 = df_valid2.drop(['Event Name','Repeat Instrument','Repeat Instance'], axis=1)

# STEP 2 - filter logs for valid pts, contact log rows, tech support contacts
logs_valid = logs[logs['Record ID'].isin(df_valid2['Record ID'])]
logs_valid = logs_valid[logs_valid['Event Name'] == 'Patient Contact']

# WE ARE NOW USING ALL REASONS FOR CONTACT

# reasons = ['Tech support for reason other than data sync', 'Patient not syncing data']
# logs_valid = logs_valid[logs_valid['Reason for contact'].isin(reasons)]

# STEP 3 - convert DT columns and merge all preprocessed data into 1 df
df_valid2['Date of scheduled PFA'] = pd.to_datetime(df_valid2['Date of scheduled PFA'])
logs_valid['Date/time of contact'] = pd.to_datetime(logs_valid['Date/time of contact'])

final_logs_df = logs_valid.merge(
    df_valid2,
    on='Record ID',
    how='left'
)

# misc column operations for ease
final_logs_df = final_logs_df.drop(['Event Name', 'Repeat Instrument', 'Repeat Instance', 
                'Study arm (use this field)', 'Unnamed: 7', 'Unnamed: 19', 'Unnamed: 22', 
                'This form complete?', 'Complete?_x', 'Date of scheduled PFA_x', 'Complete?_y'], axis=1)

final_logs_df.rename(columns={'Date of scheduled PFA_y': 'PFA_DT', 
                         'Date/time of contact': 'contact_DT', 
                         'Age in years': 'Age'}, inplace=True)


final_logs_df.to_csv("data/preproc_data.csv")
print("Data Pre-Processing Complete | New Data Saved")