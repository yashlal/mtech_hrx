# Instructions for HRX Abstract Code
Author - Yash Lal

Date - 5/14/2026

Contact regarding issues - lalyash1804@gmail.com

## Step 1 - Setup Folder
Create a folder to hold all the code and data

Put the `main.py` and `preprocess.py` files in this new folder

Make two different subfolders named `data` and `out`

## Step 2 - Download Data 

When navigating to a Report, there is a section on the left side with all the Reports for easy access. Simply click there for the instructions below.

### Part 1 - Download Contact Logs
Open the RedCap

Go to **Report #6 "Patient Contact Logs"**

Hit Export Data

On the left, hit "CSV / Microsoft Excel (Labels)"

Then, hit Export Data button (bottom right)

Click the Excel icon on the next screen to download

Rename the downloaded file `contact_logs_raw.csv`

Place it under your `data` subfolder

### Part 2 - Download Coaching Call Logs
Open the RedCap

Go to **Report #10 "Coaching Calls"**

Hit Export Data

On the left, hit "CSV / Microsoft Excel (Labels)"

Then, hit Export Data button (bottom right)

Click the Excel icon on the next screen to download

Rename the downloaded file `coach_raw.csv`

Place it under your `data` subfolder

### Part 2 - Download Patient Info
Open the RedCap

Go to **Report #5 "HRX Abstract"**

Hit Export Data

On the left, hit "CSV / Microsoft Excel (Labels)"

Then, hit Export Data button (bottom right)

Click the Excel icon on the next screen to download

Rename the downloaded file `data_raw.csv`

Place it under your `data` subfolder

## Step 3 - Running the preprocessing
To pre-process the data, simply run the `preprocess.py` file

There should now be two new files under the `data` folder named `preproc_coach.csv` and `preproc_data.csv`

## Step 4 - Generating the summary statistics
To generate the statistics, simply run the `main.py` file after ensuring the pre-processing has generated the above files.

Make sure your `out` folder exists or the code won't work.

Now, under the `out` folder, you can find a bunch of txt files with your results!

## Step 5 - Interpreting results
This section is a guide to understanding the output of the last step.

You should have 7 output files. Note, all p-values are generated using 2-Way Mann-Whitney U test. ALso, IQR = inter-quartile range below.

### 1. `interv_tech_min.txt`
This file gives you the statistics for total minutes spent on tech calls for intervention patients. The statistics are medians with the IQR in parentheses.

### 2. `interv_num_calls.txt`
This file gives you the statistics for number of tech calls for intervention patients. The statistics are mean with the STD in parentheses.

### 3. `all_accrual.txt`
This file gives you the statistics for the contact logs for patient accrual ("Calling to assess interest in study", "Reminder to fill out surveys", "Reminding patient of randomization"). This is based on number of calls and reports median with IQR. This file uses all patients regardless of randomization arm (but all patients in this analysis **have been randomized**). 

### 4. `control_tech_min.txt`
This file is the same as 1 but for the control group.

### 5. `control_num_call.txt`
This file is the same as 2 but for the control group.

### 6. `coach_mean_dur.txt`
This file presents summary stats on the mean duration of the weekly (nurse-based) coaching calls. This one is calculated a little differently. Since different patients may be in different weeks of the program, I first calculated the mean call time amongst coaching calls **per each patient**. Then, I do the usual method on this numerical column to calculate the summary statistics with median and IQR for various phenotypes.

### 7. `arms_comparison.txt`
This file contains p-values for comparing the intervention and control arms of the study, both by number of tech calls and total duration of tech calls. The statistic is the stat value for the MW U test in case you want it. This file does NOT have the median/IQR or mean/STD values of the two datasets being compared but they can be found in the files described above.