#
# 2025/6/10
# from chatGPT 
# 2025/6/12 
#  working when using import msvcrt

import msvcrt

# 檢查是否為有效 16 進位字元
def is_hex_char(c):
    return c.isdigit() or c.lower() in 'abcdef'

# beep 聲
def beep():
    print('\a', end='', flush=True)

# CRC8 運算 (多項式: x^8 + x^2 + x + 1 -> 0x07)
def crc8(data):
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

# 讀取並驗證使用者輸入
def read_hex_input():
    print("請輸入 16 進位字元 (1-9, a-f, A-F)，按 Enter 結束：")
    hex_chars = ''
    while True:
        ch = msvcrt.getch()
        if ch in (b'\r', b'\n'):
            break
        try:
            char = ch.decode('utf-8')
        except UnicodeDecodeError:
            beep()
            continue

        if is_hex_char(char):
            hex_chars += char
            print(char, end='', flush=True)
            if len(hex_chars.replace(' ', '')) % 2 == 0:
                print(' ', end='', flush=True)
        else:
            beep()
    return hex_chars.replace(' ', '')

# 將 hex 字串轉為 byte list
def convert_to_byte_list(hex_string):
    byte_list = []
    for i in range(0, len(hex_string), 2):
        if i + 1 < len(hex_string):
            byte = int(hex_string[i:i+2], 16)
            byte_list.append(byte)
    return byte_list

# 主控流程
def main():
    hex_string = read_hex_input()
    byte_list = convert_to_byte_list(hex_string)
    crc = crc8(byte_list)
    byte_list.append(crc)

    print("\n\n轉換結果 (含 CRC8)：")
    print([f"0x{b:02X}" for b in byte_list])

if __name__ == '__main__':
    main()
