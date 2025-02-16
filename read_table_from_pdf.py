import camelot  # For table extraction
import pandas as pd

#%% Read from Camelot
def process_pdf_with_tables(pdf_path):
    """Processes a PDF with tables, extracts data, and interacts with Gemini."""

    try:
        # 1. Table Extraction using Camelot
        tables = camelot.read_pdf(pdf_path, pages="1-end", flavor="stream",row_tol=10)
            
        # Step 1: Identify all unique columns across tables
        all_columns = set()
        dfs = []

        for table in tables:
            df = table.df
            all_columns.update(df.columns)  # Collect all column names
            dfs.append(df)

        # Convert set to sorted list to maintain order
        all_columns = sorted(all_columns)

        # Step 2: Standardize all DataFrames
        df_list = []
        for df in dfs:
            df = df.reindex(columns=all_columns, fill_value=None)  # Add missing columns
            df_list.append(df)

        # Step 3: Concatenate all DataFrames
        final_df = pd.concat(df_list, ignore_index=True)
        
    except:
        return "No tables found in the PDF."

    return final_df

#%% merge the rows
def merge_split_rows(df):
    new_rows = []
    for row in df.values:
        if row[0].strip() == "" or row[1].strip() == "":  # If the first column is empty, it's likely a continuation
            print('row: ', row)
            try:
                print('last row: ', new_rows[-1])
                new_rows[-1] = [new_rows[-1][i] + " " + row[i] for i in range(len(row))]
            except:
                print('error occured, ignore')
        else:
            new_rows.append(row)
    return pd.DataFrame(new_rows, columns=df.columns)

#%% Iterative merging
def clean_text(text):
    if isinstance(text, str):
        return " ".join(text.split()).strip()  # Removes newlines & extra spaces
    return text  # Return unchanged if not a string

#%% Read tables
pdf_file_path_1 = "URS_02_A_Test_Prabhat_training_Record.pdf"
pdf_file_path_2 = "URS_02_B_Test_Sainath_Training_record.pdf"

df_1 = process_pdf_with_tables(pdf_file_path_1)

df_1 = merge_split_rows(df_1)

df_1 = df_1.applymap(clean_text)



