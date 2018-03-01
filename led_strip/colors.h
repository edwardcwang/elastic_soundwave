#ifndef __COLORS
#define __COLORS

inline uint8_t color_blue(uint32_t color) {
  return color & 0xff;
}

inline uint8_t color_green(uint32_t color) {
  return (color & (0xff << 8)) >> 8;
}

inline uint8_t color_red(uint32_t color) {
  return (color & (0xff << 16)) >> 16;
}

uint8_t interpolate(int step, int max, uint8_t start, uint8_t end) {
  return (end - start)*((float)step / max) + start;
}

/**
 * Generate a heatmap
 * intensity - 0 to 255 of the red in the center
 */
uint32_t heatmapColour(int i, int intensity, int num_leds) {
  uint8_t centre_red = intensity;
  uint8_t centre_green = 0xff - intensity;
  uint8_t centre_blue = 0;

  uint8_t edge_red = 0;
  uint8_t edge_green = 0;
  uint8_t edge_blue = 0xff;

  int step = 0;
  if (i < (num_leds / 2)) {
    step = i;
  } else {
    step = (num_leds / 2) - (i - (num_leds/2));
  }
  //~ Serial.print("centre_red = ");
  //~ Serial.println(centre_red);
  //~ Serial.print("centre_blue = ");
  //~ Serial.println(centre_blue);
  uint8_t this_red = interpolate(step, num_leds/2, edge_red, centre_red);
  uint8_t this_green = interpolate(step, num_leds/2, edge_green, centre_green);
  uint8_t this_blue = interpolate(step, num_leds/2, edge_blue, centre_blue);
  return ((uint32_t)this_red << 16) | ((uint32_t)this_green << 8) | ((uint32_t)this_blue);
}

#endif
