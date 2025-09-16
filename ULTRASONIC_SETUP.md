# Ultrasonic Sensor Setup for Raspberry Pi

This document explains how to set up and use the ultrasonic sensor detection system for the Recycle Arcade project.

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- HC-SR04 Ultrasonic Sensor
- Jumper wires
- Breadboard (optional)

## Wiring Diagram

Connect the HC-SR04 sensor to your Raspberry Pi as follows:

```
HC-SR04    →    Raspberry Pi
VCC        →    5V (Pin 2)
GND        →    GND (Pin 6)
Trig       →    GPIO 18 (Pin 12)
Echo       →    GPIO 24 (Pin 18)
```

## Software Installation

1. Install the required Python package:
```bash
pip install RPi.GPIO
```

Or install from the requirements file:
```bash
pip install -r requirements_ultrasonic.txt
```

2. Make sure your Raspberry Pi has the necessary permissions for GPIO access.

## Usage

1. Run the ultrasonic detection script:
```bash
python ultrasonic_detector.py
```

2. The script will continuously monitor for obstacles within the detection distance (default: 30 cm).

3. When an obstacle is detected, the main application will launch automatically.

## Configuration

You can modify the following parameters in `ultrasonic_detector.py`:

- `TRIG_PIN`: GPIO pin for trigger (default: 18)
- `ECHO_PIN`: GPIO pin for echo (default: 24)
- `DETECTION_DISTANCE`: Distance threshold in cm (default: 30)
- `LAUNCH_COOLDOWN`: Minimum seconds between launches (default: 5)

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Make sure your user is in the `gpio` group:
   ```bash
   sudo usermod -a -G gpio $USER
   ```

2. **Sensor not responding**: Check your wiring and ensure the sensor is powered correctly.

3. **Inconsistent readings**: Make sure the sensor is not too close to walls or other objects that might cause interference.

### Testing the Sensor

You can test the sensor independently by running a simple distance measurement:

```python
import RPi.GPIO as GPIO
import time

TRIG_PIN = 18
ECHO_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_distance():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

try:
    while True:
        distance = measure_distance()
        print(f"Distance: {distance} cm")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
```

## Advantages of Ultrasonic Detection

- **Lower power consumption**: No camera processing required
- **More reliable**: Not affected by lighting conditions
- **Simpler setup**: Fewer dependencies and configuration
- **Faster response**: Direct distance measurement without image processing
- **Privacy-friendly**: No video capture or processing
- **Cost-effective**: Cheaper than camera-based solutions

## Integration with Arcade System

The ultrasonic detector integrates seamlessly with the arcade system:

1. When an obstacle is detected, it launches `main.py` automatically
2. The main application provides a game selection dashboard
3. Users can choose from 3 games: Asteroid Game, Cycle Forest, or Traffic Dash
4. All existing games work without modification
5. The cooldown system prevents multiple rapid launches
