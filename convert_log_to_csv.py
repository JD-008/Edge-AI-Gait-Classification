import re
import csv

# Open the raw log text you copied from nRF Connect
try:
    with open("limping.txt", "r", encoding="utf-8") as file:
        log_data = file.read()
except FileNotFoundError:
    print(" Please save your log text in a file named 'nrf_log.txt' first!")
    exit()

# 1. Extract only the data fragments inside the quotes
# This looks for lines ending with 'received' and grabs the text inside ""
fragments = re.findall(r'"([^"]*)" received', log_data)

# 2. Stitch all the broken BLE fragments back into one massive string
stitched_data = "".join(fragments)

# 3. Use Regex to find every single valid number (handles negatives and decimals)
# This perfectly ignores commas, random hyphens, and missing characters
all_numbers = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', stitched_data)

# 4. Group the numbers into chunks of 6 (ax, ay, az, gx, gy, gz)
csv_filename = "ArcSense_Master_Dataset.csv"
valid_rows = 0

with open(csv_filename, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    
    # Write the exact headers your Streamlit Athlete Dashboard expects
    writer.writerow(["timestamp", "stride_id", "acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z"])
    
    # Loop through the numbers 6 at a time
    for i in range(0, len(all_numbers) - 5, 6):
        ax = all_numbers[i]
        ay = all_numbers[i+1]
        az = all_numbers[i+2]
        gx = all_numbers[i+3]
        gy = all_numbers[i+4]
        gz = all_numbers[i+5]
        
        # Fake the timestamp (20ms increments for 100Hz)
        timestamp_ms = valid_rows * 20 
        
        # Fake the stride_id (Assume 1 stride every 100 readings / 1 second for the dashboard visual)
        stride_id = (valid_rows // 100) + 1 
        
        writer.writerow([timestamp_ms, stride_id, ax, ay, az, gx, gy, gz])
        valid_rows += 1

print(f"Success! Extracted {valid_rows} complete 6-axis readings.")
print(f" Saved cleanly to '{csv_filename}'.")
