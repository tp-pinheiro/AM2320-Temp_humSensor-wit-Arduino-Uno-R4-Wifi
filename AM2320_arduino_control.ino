#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(100000);  // AM2320 is sensitive to high speeds
}

bool readAM2320(float &humidity, float &temperature) {
  // Wake-up pulse
  Wire.beginTransmission(0x5C);
  Wire.endTransmission();
  delay(3);

  // Send read command: function 0x03, start at 0x00, read 4 bytes
  Wire.beginTransmission(0x5C);
  Wire.write(0x03);
  Wire.write(0x00);
  Wire.write(0x04);
  if (Wire.endTransmission() != 0) {
    return false;  // command error
  }

  delay(3);

  // Request 6 bytes: [func][len][Hh][Hl][Th][Tl]
  Wire.requestFrom(0x5C, 6);
  if (Wire.available() != 6) {
    return false;  // read error
  }

  uint8_t func = Wire.read();
  uint8_t len  = Wire.read();
  uint8_t Hh   = Wire.read();
  uint8_t Hl   = Wire.read();
  uint8_t Th   = Wire.read();
  uint8_t Tl   = Wire.read();

  // Basic validation
  if (func != 0x03 || len != 0x04) {
    return false;
  }

  // Convert values
  uint16_t rawH = (Hh << 8) | Hl;
  uint16_t rawT = (Th << 8) | Tl;

  humidity    = rawH / 10.0;
  temperature = rawT / 10.0;

  return true;
}

void loop() {
  float h, t;

  if (readAM2320(h, t)) {
    Serial.print("Temp: ");
    Serial.print(t);
    Serial.print(" °C\t");

    Serial.print("Humidity: ");
    Serial.print(h);
    Serial.println(" %");
  } else {
    Serial.println("Sensor read failed");
  }

  delay(2000);
}
