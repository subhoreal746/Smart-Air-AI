import pandas as pd
import numpy as np

def clean_data(input_file, output_file):
    # 1. Load the data
    df = pd.read_csv(input_file)
    
    if df.empty:
        print("CSV is empty yet!")
        return

    # 2. Forward Fill any remaining gaps (just in case)
    df.ffill(inplace=True)

    # 3. Create a 'Target' column for Machine Learning
    # We label anything above 0.7V as '1' (Event) and below as '0' (Normal)
    df['is_spike'] = (df['gas_voltage'] > 0.7).astype(int)

    # 4. Feature Engineering: Calculating the 'Slope'
    # This tells the AI how fast the gas is rising
    df['voltage_change'] = df['gas_voltage'].diff().fillna(0)

    # 5. Save the 'Clean' data for the AI to study
    df.to_csv(output_file, index=False)
    print(f"✅ Cleaned {len(df)} rows. Saved to {output_file}")

if __name__ == "__main__":
    clean_data("mac_sensor_data.csv", "cleaned_air_data.csv")
