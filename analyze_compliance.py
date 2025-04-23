import pandas as pd

def compute_compliance(reference_file, user_training_file):

    df_ref = pd.read_excel(reference_file)
    tot_training_ref = df_ref.shape[0]

    # Define column names
    columns = ['Name', 'Designation', 'Compliance Percentage', 'Count Completed',
               'Count Not Present', 'Extra Count', 'Days Available', 'Days Taken',
               'Days Late/Early']

    # Create an empty DataFrame
    final_df = pd.DataFrame(columns=columns)

    for file in user_training_file:

        df_user = pd.read_excel(file)

        designation = df_user['Designation'][0]

        req_train = df_ref[['ID','Title',designation]]
        req_train = req_train[req_train.iloc[:,2]=='Yes']

        # id_counts = df_user['ID'].value_counts()

        # Count of all trainings which are part of the reference training
        count_completed = int(df_ref['ID'].isin(df_user['ID']).sum())
        print(count_completed)

        # count of all training not done
        count_not_present = int((~df_ref['ID'].isin(df_user['ID'])).sum())
        print(count_not_present)

        # Count of extra training which are not part of reference
        extra_count = int((~df_user['ID'].isin(df_ref['ID'])).sum())
        print(extra_count)

        percentage_compliance = count_completed/tot_training_ref

        # Convert the date columns to datetime format

        # Function to clean the date by removing timezone info
        def clean_datetime(date_str):
            return date_str.split(' (')[0]  # Remove everything after ' (' (including timezone)

        # Apply the function to clean dates
        df_user['Assigned Date'] = df_user['Assigned Date'].apply(clean_datetime)
        df_user['Due Date'] = df_user['Due Date'].apply(clean_datetime)
        df_user['Completed Date'] = df_user['Completed Date'].apply(clean_datetime)

        # Convert cleaned dates to datetime
        df_user['Assigned Date'] = pd.to_datetime(df_user['Assigned Date'], format='%Y-%m-%d %H:%M')
        df_user['Due Date'] = pd.to_datetime(df_user['Due Date'], format='%Y-%m-%d %H:%M')
        df_user['Completed Date'] = pd.to_datetime(df_user['Completed Date'], format='%Y-%m-%d %H:%M')

        # Calculate required values
        days_available = (df_user['Due Date'] - df_user['Assigned Date']).dt.days  # New column
        days_taken = (df_user['Completed Date'] - df_user['Assigned Date']).dt.days
        days_late_early = (df_user['Completed Date'] - df_user['Due Date']).dt.days

        # Reorder columns to make "Days Available" the first column
        # df_user = df_user[['Days Available', 'Days Taken', 'Days Late/Early']]

        # Display results
        # print(df_user[['Days Available', 'Days Taken', 'Days Late/Early']])

        # mean_val = df_user[['Days Available', 'Days Taken', 'Days Late/Early']].mean()

        # Create a new row as a dictionary
        new_row = {
            'Name': df_user.iloc[0,0] ,
            'Designation': designation,
            'Compliance Percentage': percentage_compliance,
            'Count Completed': count_completed,
            'Count Not Present': count_not_present,
            'Extra Count': extra_count,
            'Days Available': days_available.mean(),
            'Days Taken': days_taken.mean(),
            'Days Late/Early': days_late_early.mean()
        }

        # Append to DataFrame
        # final_df = pd.concat([final_df, pd.DataFrame([new_row])], ignore_index=True)
        if not final_df.empty:  # Check if final_df is empty
            final_df = pd.concat([final_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            final_df = pd.DataFrame([new_row])  # Create a new DataFrame if final_df is empty

    return final_df

if __name__ == '__main__':

    reference_file = 'URS_02_A_Referene_Training_Curriculum.xlsx'

    file_1 = 'URS_02_A_Test_Prabhat_training_record.xlsx'
    file_2 = 'URS_02_B_Test_Sainath_training_record.xlsx'

    user_training_file = [file_1,file_2]

    final_df = compute_compliance(reference_file, user_training_file)
    print(f" final_df:  {final_df}")

# compliance_df = compute_compliance()


