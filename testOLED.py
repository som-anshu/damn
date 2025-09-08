# This test code has been updated to use the Adafruit CircuitPython library,
# which is modern and well-supported on the Raspberry Pi.
# It displays key system information and updates every second.

import time
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

def main():
    try:
        # --- Initialization ---
        # Create the I2C interface using the board's default SCL and SDA pins.
        i2c = busio.I2C(SCL, SDA)

        # Create the SSD1306 OLED class.
        # The first two parameters are the pixel width and height.
        # The I2C address 0x3C is standard for these displays.
        disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

        # Clear the display.
        disp.fill(0)
        disp.show()

        # --- Drawing Setup ---
        # Create a blank image for drawing in 1-bit color.
        image = Image.new("1", (disp.width, disp.height))

        # Get a drawing object to draw on the image.
        draw = ImageDraw.Draw(image)

        # Load a font.
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except IOError:
            font = ImageFont.load_default()
            print("Default font not found, using built-in font.")

        # --- Main Loop ---
        print("Displaying system stats. Press Ctrl+C to exit.")
        while True:
            # Draw a black filled box to clear the image.
            draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)

            # Get system stats using shell commands
            cmd = "hostname -I | cut -d' ' -f1"
            IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
            CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB\", $3,$2 }'"
            MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB %s", $3,$2,$5}\''
            Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

            # Write text lines
            padding = -2
            top = padding
            draw.text((0, top), "IP: " + IP, font=font, fill=255)
            draw.text((0, top + 12), CPU, font=font, fill=255)
            draw.text((0, top + 24), MemUsage, font=font, fill=255)
            draw.text((0, top + 36), Disk, font=font, fill=255)
            draw.text((0, top + 52), "--------------------", font=font, fill=255)


            # Display the image.
            disp.image(image)
            disp.show()
            time.sleep(1)

    except (ValueError, OSError) as e:
        print(f"An error occurred: {e}")
        print("Please check your wiring and ensure the I2C interface is enabled.")
        print("Run 'sudo i2cdetect -y 1' to confirm the display is detected.")
    except KeyboardInterrupt:
        # Clear the display on exit
        try:
            disp.fill(0)
            disp.show()
            print("\nScript terminated. Display cleared.")
        except NameError:
            pass

if __name__ == "__main__":
    main()

