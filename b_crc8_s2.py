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

def send_receive_serial(byte_list):
    """Sends a byte list over serial, receives a response, and prints it with CRC8."""
    try:
        with serial.Serial(COM_PORT, BAUD_RATES, timeout=1) as ser:
            # Send the byte list with a line feed
            ser.write(bytearray(byte_list) + b'\n')

            # Read response until CR or LF
            received_data = ser.read_until(b'\r\n')
            
            # Process and print the received data
            if received_data:
                # Strip CR/LF and convert to list of ints
                received_bytes = [b for b in received_data.strip()]
                
                # Calculate CRC8 and append
                crc = crc8(received_bytes)
                received_bytes.append(crc)
                
                # Print the result
                print("\nReceived Data:")
                print(format_output(received_bytes))
            else:
                print("\nNo data received from serial port.")

    except serial.SerialException as e:
        print(f"\nSerial port error: {e}")

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
    send_receive_serial(byte_list)

if __name__ == "__main__":
    main()