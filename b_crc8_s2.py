COM_PORT = 'COM3'
BAUD_RATES = 115200

#
# 2025/6/10
# from Grok 
#  完全對


import sys
import os
import time
import serial
if os.name == 'nt': # is nt
    import msvcrt

else:
    import tty
    import termios

def beep():
    """Generate a beep sound."""
    print('\a', end='', flush=True)

def is_valid_hex(char):
    """Check if character is valid hexadecimal (0-9, a-f, A-F)."""
    return char.lower() in '0123456789abcdef'

def get_char():
    """Get a single character from input with handling for different OS."""
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8')
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char

def input_hex():
    """Handle hex input with validation and formatting."""
    input_str = ""
    count = 0
    while True:
        char = get_char()
        
        # Handle enter key (CR or LF)
        if char in '\r\n':
            if count % 2 == 0 and count > 0:  # Only accept if even number of chars
                break
            else:
                beep()
                continue
                
        # Handle backspace
        if char == '\b':
            if input_str:
                input_str = input_str[:-1]
                count -= 1
                print(f'\b \b', end='', flush=True)
            continue
            
        # Validate hex character
        if not is_valid_hex(char):
            beep()
            continue
            
        # Add valid character
        input_str += char.lower()
        count += 1
        print(char.lower(), end='', flush=True)
        
        # Add space after every 2 characters
        if count % 2 == 0:
            input_str += ' '
            print(' ', end='', flush=True)
    
    return input_str.strip()

def hex_to_bytes(hex_str):
    """Convert hex string to byte list."""
    # Remove spaces and convert pairs to bytes
    hex_str = hex_str.replace(' ', '')
    return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]

def crc8(data):
    """Calculate CRC8 checksum."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
        crc &= 0xFF
    return crc

def format_output(byte_list):
    """Format the byte list as hex string."""
    return ' '.join(f'{b:02x}' for b in byte_list)

def send_serial(ser, byte_list):
    """Sends a byte list over the serial port."""
    try:
        ser.write(bytearray(byte_list) + b'\n')
    except serial.SerialException as e:
        print(f"\nSerial port error during send: {e}")

def receive_serial(ser):
    """Receives data from the serial port, processes it, and prints the result."""
    try:
        received_data = ser.read_until(b'\r\n')

        if received_data:
            received_bytes = [b for b in received_data.strip()]

            if len(received_bytes) > 1:
                data_to_check = received_bytes[:-1]
                received_crc = received_bytes[-1]
                calculated_crc = crc8(data_to_check)

                if calculated_crc == received_crc:
                    print("\nReceived Data:")
                    print(format_output(data_to_check))
                else:
                    print("\nCRC 8 error")
            else:
                print("\nReceived data is too short for CRC check.")
        else:
            print("\nNo data received from serial port.")

    except serial.SerialException as e:
        print(f"\nSerial port error during receive: {e}")

def main():
    """Main function to coordinate the process."""
    print("Enter hex digits (0-9, a-f, A-F), press Enter to finish:")
    
    # Get input
    hex_input = input_hex()
    print # Convert to newline character
    
    # Convert to bytes
    byte_list = hex_to_bytes(hex_input)
    
    # Calculate CRC8 and append
    crc = crc8(byte_list)
    byte_list.append(crc)
    
    # Print result
    print("\nOutput:")
    print(format_output(byte_list))

    # Send and receive over serial
    try:
        with serial.Serial(COM_PORT, BAUD_RATES, timeout=1) as ser:
            send_serial(ser, byte_list)
            receive_serial(ser)
    except serial.SerialException as e:
        print(f"\nSerial port error: {e}")

if __name__ == "__main__":
    main()