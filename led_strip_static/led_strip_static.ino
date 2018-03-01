// LED strip that doesn't use the computer and just uses the LED heatmap to
// change colours periodically.

// SW SPI
/*
#define CLK P3_7
#define DATA P8_1
*/
// HW SPI
#define CLK P3_2
#define DATA P3_0

int adc1_pin = P7_0;

#include "Adafruit_DotStar.h"

int num_leds = 83; // verified by counting twice
//SW SPI
//Adafruit_DotStar strip = Adafruit_DotStar(num_leds, DATA, CLK, DOTSTAR_BGR);
//HW SPI
Adafruit_DotStar strip = Adafruit_DotStar(num_leds, DOTSTAR_BGR);
void setup() {
  pinMode(RED_LED, OUTPUT);
  pinMode(PUSH2, INPUT_PULLUP);
  pinMode(adc1_pin, INPUT);

  delay(500);
  Serial.begin(115200);

  strip.begin();
  strip.show();
  rainbow_step();
}

void cyan() {
  int blue = 0;
  int green = 0;
  while(1) {
    if (blue < 255) {
      blue += 20;
      if (blue > 255) blue = 255;
    } else {
      if (green < 255) {
        green += 20;
        if (green > 255) green = 255;
      } else {
        blue = 0; green = 0;
      }
    }

    strip.setPixelColor(0, 0x001100);
    strip.setPixelColor(1, 0, green, blue);
    strip.show();
    delay(60);
  }
}

uint32_t rainbow[] = {
  0xff0000, // red
  0xE2571E, // orange-ish red
  0xFF7F00, // orange
  0xFFFF00, // yellow
  0x80FF00,
  0x00FF00, // green
  0x96bf33, // some green
  0x0000FF, // blue
  0x4B0082, // indigo
  0x2600C1,
  0x8B00FF, // violet
};
int rainbow_size = 11;

int count = 0;
void rainbow_step() {
    for (int i = 0; i < num_leds; i++) {
      strip.setPixelColor(i, rainbow[(i + count) % rainbow_size]);
    }
    strip.show();
    count++;
}

#include "colors.h"

void heatmap(int intensity) {
  for (int i = 0; i < num_leds; i++) {
    uint32_t color = heatmapColour(i, intensity, num_leds);
    strip.setPixelColor(i, color);
  }
  strip.show();
}

int heat = 0;
int increasing = 1;
void loop() {
  //uint8_t counter = 0;
  
  while(1) {
    for (int i = 0; i <= 255; i += 10) {
      heatmap(i);
      //Serial.println(i);
      delay(250);
    }
    for (int i = 255; i >= 0; i -= 10) {
      heatmap(i);
      delay(250);
    }
  }
}
