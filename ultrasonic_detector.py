#!/usr/bin/env python3
"""
Ultrasonic Sensor Obstacle Detection for Raspberry Pi
Replaces camera-based YOLO detection with HC-SR04 ultrasonic sensor
"""

import RPi.GPIO as GPIO
import time
import subprocess
import sys
import os
import signal

# GPIO pin configuration for HC-SR04 ultrasonic sensor
TRIG_PIN = 18  # GPIO pin for trigger
ECHO_PIN = 24  # GPIO pin for echo

# Detection parameters
DETECTION_DISTANCE = 30  # Distance in cm to trigger detection
OBSTACLE_DETECTED = False
LAST_LAUNCH_TIME = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def cleanup_gpio():
    """Clean up GPIO pins on exit"""
    GPIO.cleanup()
    print("GPIO cleanup completed")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nStopping ultrasonic detection...")
    cleanup_gpio()
    sys.exit(0)

def measure_distance():
    """
    Measure distance using HC-SR04 ultrasonic sensor
    Returns distance in centimeters
    """
    try:
        # Send trigger pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(TRIG_PIN, False)
        
        # Wait for echo to start
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
        
        # Wait for echo to end
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
        
        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Speed of sound = 343 m/s, convert to cm
        distance = round(distance, 2)
        
        return distance
    
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return -1

def launch_main():
    """Launch the main application when obstacle is detected"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    
    if os.path.exists(main_script):
        print("Obstacle detected! Launching main application...")
        subprocess.Popen([sys.executable, main_script])
        sys.exit(0)
    else:
        print(f"Error: {main_script} not found!")

def main():
    """Main detection loop"""
    global OBSTACLE_DETECTED, LAST_LAUNCH_TIME
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting ultrasonic obstacle detection...")
    print(f"Detection distance: {DETECTION_DISTANCE} cm")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        while True:
            distance = measure_distance()
            
            if distance > 0:
                print(f"Distance: {distance} cm", end="")
                
                # Check if obstacle is detected
                if distance <= DETECTION_DISTANCE:
                    current_time = time.time()
                    
                    if not OBSTACLE_DETECTED and (current_time - LAST_LAUNCH_TIME) > LAUNCH_COOLDOWN:
                        OBSTACLE_DETECTED = True
                        LAST_LAUNCH_TIME = current_time
                        print(" - OBSTACLE DETECTED!")
                        launch_main()
                    else:
                        print(" - Obstacle detected (cooldown active)")
                else:
                    OBSTACLE_DETECTED = False
                    print(" - No obstacle")
            else:
                print("Error reading sensor")
            
            # Small delay to prevent excessive readings
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nStopping detection...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        cleanup_gpio()

if __name__ == "__main__":
    main()
