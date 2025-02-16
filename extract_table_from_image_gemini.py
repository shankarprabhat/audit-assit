import pandas as pd
import io
from PIL import Image
import pytesseract

def extract_table_from_image(image_path):
    """
    Extracts a table from an image and returns it as a Pandas DataFrame.

    Args:
        image_path: Path to the image file.

    Returns:
        A Pandas DataFrame representing the extracted table, or None if 
        extraction fails.  Returns an error message string if pytesseract
        is not installed.
    """

    try:
        # Perform OCR using pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)

        # Basic text processing to clean up OCR output (improve as needed)
        lines = text.strip().split('\n')
        data = []
        for line in lines:
            # Split each line by spaces, but handle multiple spaces and empty strings
            row = [x.strip() for x in line.split() if x.strip()]  
            if row: # Skip empty rows
              data.append(row)


        if not data:  # Check if any data was extracted
            return pd.DataFrame() # Return empty DataFrame if no data

        # Identify header row (first row assumed to be the header)
        header = data[0]

        # Extract data rows, handling potential misalignment issues
        table_data = []
        for i in range(1, len(data)):  # Start from the second row
          row_data = {}
          row = data[i]

          # Improved handling of misaligned columns
          col_index = 0
          for j in range(len(header)):
              if col_index < len(row) and header[j] != "": # Check if column exists
                row_data[header[j]] = row[col_index] # Assign column value
                col_index += 1
              else:
                row_data[header[j]] = "" # Assign empty string if column missing

          table_data.append(row_data)

        df = pd.DataFrame(table_data)

        # Further data cleaning (replace checkmarks with Yes/No)
        df.replace({'✓': 'Yes', '□': 'No', '☑': 'Yes'}, inplace=True)  # Add more symbols if needed

        return df

    except FileNotFoundError:
        return "Error: Image file not found."
    except Exception as e:
        return f"An error occurred: {e}"
    except ImportError:
       return "Error: pytesseract is not installed.  Install it with 'pip install pytesseract'"


# Example usage:
image_path = 'your_image.png'  # Replace with the actual path to your image
df = extract_table_from_image(image_path)

if isinstance(df, pd.DataFrame):
  if df.empty:
    print("No data was extracted from the image.")
  else:
    print(df)
    # Save to CSV:
    df.to_csv('extracted_table.csv', index=False)
    print("Table saved to extracted_table.csv")
elif isinstance(df, str):  # Check for error message
    print(df)
else:
  print("An unknown error occurred.")
