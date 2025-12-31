import pandas as pd
import numpy as np

def clean_data(input_file, output_file):
    
    df = pd.read_csv(input_file)
    
    if df.empty:
        print("CSV is empty yet!")
        return

    
    df.ffill(inplace=True)

    
    df['is_spike'] = (df['gas_voltage'] > 0.7).astype(int)

    
    df['voltage_change'] = df['gas_voltage'].diff().fillna(0)

    
    df.to_csv(output_file, index=False)
    print(f"Cleaned {len(df)} rows. Saved to {output_file}")

if __name__ == "__main__":
    clean_data("mac_sensor_data.csv", "cleaned_air_data.csv")
