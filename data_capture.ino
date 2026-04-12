#include <bluefruit.h>
#include <LSM6DS3.h>
#include <Wire.h>

// Initialize the onboard IMU
LSM6DS3 myIMU(I2C_MODE, 0x6A);

// Create the BLE UART service
BLEUart bleuart;

unsigned long previousMillis = 0;
const long interval = 10; // 10ms delay = 100Hz Sampling Rate

void setup() {
  Serial.begin(115200);

  // 1. Boot up the IMU
  if (myIMU.begin() != 0) {
    Serial.println("IMU initialization failed!");
    // Don't freeze completely, just warn.
  }

  // 2. Boot up the native Bluefruit BLE
  Bluefruit.begin();
  Bluefruit.setTxPower(4); // Max transmission power
  Bluefruit.setName("ArcSense");

  // 3. Configure BLE UART
  bleuart.begin();

  // 4. Start advertising
  startAdv();
  Serial.println("Arc Sense BLE active. Waiting for connection...");
}

void startAdv(void) {
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();

  Bluefruit.Advertising.addService(bleuart);
  Bluefruit.Advertising.addName();

  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244);
  Bluefruit.Advertising.setFastTimeout(30);
  Bluefruit.Advertising.start(0);
}

void loop() {
  if (Bluefruit.connected()) {
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;

      float ax = myIMU.readFloatAccelX();
      float ay = myIMU.readFloatAccelY();
      float az = myIMU.readFloatAccelZ();
      float gx = myIMU.readFloatGyroX();
      float gy = myIMU.readFloatGyroY();
      float gz = myIMU.readFloatGyroZ();

      String imuData = String(ax, 2) + "," + String(ay, 2) + "," + String(az, 2) + "," +
                       String(gx, 2) + "," + String(gy, 2) + "," + String(gz, 2) + "\n";

      bleuart.print(imuData);
    }
  }
}
