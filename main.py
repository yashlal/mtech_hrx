import pandas as pd
import numpy as np
from scipy.stats import *

all_reasons = ["Patient not syncing data", 
                "Tech support for reason other than data sync",
                "Calling to assess interest in study", 
                "Reminder to fill out surveys",
                "Reminding patient of randomization"]

accrual_reasons = ["Calling to assess interest in study",
                    "Reminder to fill out surveys",
                    "Reminding patient of randomization"]

tech_reasons = ["Patient not syncing data", 
                "Tech support for reason other than data sync"]


def df_setup(df_input, arm = 'both', reasons = all_reasons, log_type = 'contact'):
    df = df_input.copy()

    if log_type == 'contact':
        if arm != 'both':
            df = df[df['Study arm'] == arm]

        df = df[df['Reason for contact'].isin(reasons)]

        patient_df = (
            df.groupby("Record ID", dropna=False)
            .agg({
                "Time of call (in minutes)": "sum",
                "Age": "first",
                "Race": "first",
                "Sex": "first",
                "Ethnicity": "first",
                "Owns Apple Watch 5 or newer?": "first",
                "Owns iPhone XS/XR or later?": "first",
                "eHEALS score": "first",
                "Record ID": "count"   # number of calls
            })
            .rename(columns={
                "Time of call (in minutes)": "Total Call Minutes",
                "Record ID": "Number of Calls"
            })
            .reset_index(drop=True)
        )
    elif log_type == 'coach':
        patient_df = (
            df.groupby("Record ID", dropna=False)
            .agg({
                "Call Duration": "mean",
                "Age": "first",
                "Race": "first",
                "Sex": "first",
                "Ethnicity": "first",
                "Owns Apple Watch 5 or newer?": "first",
                "Owns iPhone XS/XR or later?": "first",
                "eHEALS score": "first",
                "Record ID": "count"   # number of calls
            })
            .rename(columns={
                "Call Duration": "Mean Call Duration",
                "Record ID": "Number of Calls"
            })
            .reset_index(drop=True)
        )
    else:
        raise Exception("Invalid log_type option - either use 'contact' or 'coach'") 

    return patient_df

def summarize_feature(
    df,
    feature_col,
    output_file,
    sex_col="Sex",
    race_col="Race",
    ethnicity_col="Ethnicity",
    watch_col="Owns Apple Watch 5 or newer?",
    iphone_col="Owns iPhone XS/XR or later?",
    eheals_col="eHEALS score",
    age_col="Age",
):
    """
    Writes median (Q1 - Q3) and n for:
      1. All patients
      2. Sex (Male vs Female)
      3. Race (White vs Other)
      4. Ethnicity (Hispanic/Latino vs Other)
      5. Apple Watch ownership (Yes vs No)
      6. iPhone ownership (Yes vs No)
      7. eHEALS score (Top vs Bottom 50%)
      8. Age (Top vs Bottom 50%)

    Uses Mann-Whitney U test for p-values.

    If feature_col == 'Total Call Minutes',
    only includes patients with values > 0.
    """

    # --------------------------------------------------
    # Helper functions
    # --------------------------------------------------

    lines = []

    def write(text=""):
        lines.append(text)

    def format_stats(series):
        if feature_col == "Number of Calls":
            mean = series.mean()
            std = series.std()

            return f"{mean:.2f} ({std:.2f})"

        else:
            median = series.median()
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            return f"{median:.2f} ({q1:.2f} - {q3:.2f})"

    def mann_whitney_p(group1, group2):
        if len(group1) == 0 or len(group2) == 0:
            return np.nan

        try:
            _, p = mannwhitneyu(group1, group2, alternative="two-sided")
            return p
        except:
            return np.nan

    def print_group_results(
        title,
        data,
        group_col,
        group1_name,
        group2_name,
        group1_mask,
        group2_mask,
    ):
        temp = data[[feature_col, group_col]].dropna()

        g1 = temp.loc[group1_mask(temp), feature_col]
        g2 = temp.loc[group2_mask(temp), feature_col]

        p = mann_whitney_p(g1, g2)

        write(f"\n--- {title} ---")

        write(
            f"{group1_name}: "
            f"n={len(g1)}, "
            f"{format_stats(g1)}"
        )

        write(
            f"{group2_name}: "
            f"n={len(g2)}, "
            f"{format_stats(g2)}"
        )

        write(f"p-value = {p:.4f}")

    # --------------------------------------------------
    # Filter Total Call Minutes > 0 if needed
    # --------------------------------------------------

    data = df.copy()

    if feature_col == "Total Call Minutes":
        data = data[data[feature_col] > 0]

    # --------------------------------------------------
    # 1. All patients
    # --------------------------------------------------

    overall = data[[feature_col]].dropna()[feature_col]

    write("\n======================================")
    write(f"Feature: {feature_col}")
    write("======================================")

    write("\n--- All Patients ---")
    write(f"n={len(overall)}")
    write(format_stats(overall))

    # --------------------------------------------------
    # 2. Sex
    # --------------------------------------------------

    print_group_results(
        title="Sex",
        data=data,
        group_col=sex_col,
        group1_name="Male",
        group2_name="Female",
        group1_mask=lambda x: x[sex_col].astype(str).str.lower() == "male",
        group2_mask=lambda x: x[sex_col].astype(str).str.lower() == "female",
    )

    # --------------------------------------------------
    # 3. Race
    # --------------------------------------------------

    print_group_results(
        title="Race",
        data=data,
        group_col=race_col,
        group1_name="White",
        group2_name="Other",
        group1_mask=lambda x: x[race_col].astype(str).str.lower() == "white",
        group2_mask=lambda x: x[race_col].astype(str).str.lower() != "white",
    )

    # --------------------------------------------------
    # 4. Ethnicity
    # --------------------------------------------------

    print_group_results(
        title="Ethnicity",
        data=data,
        group_col=ethnicity_col,
        group1_name="Hispanic/Latino",
        group2_name="Other",
        group1_mask=lambda x: (
            x[ethnicity_col].astype(str).str.lower()
            == "hispanic/latino"
        ),
        group2_mask=lambda x: (
            x[ethnicity_col].astype(str).str.lower()
            != "hispanic/latino"
        ),
    )

    # --------------------------------------------------
    # 5. Apple Watch
    # --------------------------------------------------

    print_group_results(
        title="Apple Watch Ownership",
        data=data,
        group_col=watch_col,
        group1_name="Yes",
        group2_name="No",
        group1_mask=lambda x: (
            x[watch_col].astype(str).str.lower() == "yes"
        ),
        group2_mask=lambda x: (
            x[watch_col].astype(str).str.lower() == "no"
        ),
    )

    # --------------------------------------------------
    # 6. iPhone Ownership
    # --------------------------------------------------

    print_group_results(
        title="iPhone Ownership",
        data=data,
        group_col=iphone_col,
        group1_name="Yes",
        group2_name="No",
        group1_mask=lambda x: (
            x[iphone_col].astype(str).str.lower() == "yes"
        ),
        group2_mask=lambda x: (
            x[iphone_col].astype(str).str.lower() == "no"
        ),
    )

    # --------------------------------------------------
    # 7. eHEALS top/bottom 50%
    # --------------------------------------------------

    temp = data[[feature_col, eheals_col]].dropna()

    median_eheals = temp[eheals_col].median()

    low = temp[temp[eheals_col] < median_eheals][feature_col]
    high = temp[temp[eheals_col] >= median_eheals][feature_col]

    p = mann_whitney_p(low, high)

    write("\n--- eHEALS Score ---")

    write(
        f"Bottom 50%: "
        f"n={len(low)}, "
        f"{format_stats(low)}"
    )

    write(
        f"Top 50%: "
        f"n={len(high)}, "
        f"{format_stats(high)}"
    )

    write(f"p-value = {p:.4f}")

    # --------------------------------------------------
    # 8. Age top/bottom 50%
    # --------------------------------------------------

    temp = data[[feature_col, age_col]].dropna()

    median_age = temp[age_col].median()

    younger = temp[temp[age_col] < median_age][feature_col]
    older = temp[temp[age_col] >= median_age][feature_col]

    p = mann_whitney_p(younger, older)

    write("\n--- Age ---")

    write(
        f"Bottom 50% (Younger): "
        f"n={len(younger)}, "
        f"{format_stats(younger)}"
    )

    write(
        f"Top 50% (Older): "
        f"n={len(older)}, "
        f"{format_stats(older)}"
    )

    write(f"p-value = {p:.4f}")

    # --------------------------------------------------
    # Write output to text file
    # --------------------------------------------------

    with open(output_file, "w") as f:
        f.write("\n".join(lines))

if __name__ == '__main__':
    date_col = "PFA_DT"
    call_dt_col = 'contact_DT'

    df = pd.read_csv("data/preproc_data.csv")
    df = df.drop('Unnamed: 0', axis=1)

    df[date_col] = pd.to_datetime(df[date_col])
    df[call_dt_col] = pd.to_datetime(df[call_dt_col])

    df1 = df_setup(df, arm = 'Intervention', reasons = tech_reasons)
    summarize_feature(df1, 'Total Call Minutes', 'out/interv_tech_min.txt')
    summarize_feature(df1, 'Number of Calls', 'out/interv_num_calls.txt')

    df2 = df_setup(df, arm = "both", reasons = accrual_reasons)
    summarize_feature(df2, 'Number of Calls', 'out/all_accrual.txt')

    df3 = df_setup(df, arm = "Control", reasons = tech_reasons)
    summarize_feature(df3, 'Total Call Minutes', 'out/control_tech_min.txt')
    summarize_feature(df3, 'Number of Calls', 'out/control_num_call.txt')

    df4 = pd.read_csv("data/preproc_coach.csv")
    df4 = df_setup(df4, log_type="coach")
    summarize_feature(df4, 'Mean Call Duration', "out/coach_mean_dur.txt")

    s1, p1 = mannwhitneyu(df1['Total Call Minutes'], df3['Total Call Minutes'])
    s2, p2 = mannwhitneyu(df1['Number of Calls'], df3['Number of Calls'])

    with open("out/arms_comparison.txt", "w") as file:
        file.write("Statistic and p-value for comparing Total Call Minutes between study arms\n")
        file.write(f"Stat {s1} | p-value {p1}\n")
        file.write("Statistic and p-value for comparing Number of Tech Calls between study arms\n")
        file.write(f"Stat {s2} | p-value {p2}")
    print("done")