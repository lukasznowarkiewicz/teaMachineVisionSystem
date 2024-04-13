import serial
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Kontrola pompy za pomocą Raspberry Pi Pico')
    parser.add_argument('-t', '--time', type=int, default=10, help='Czas działania pompy w sekundach')
    return parser.parse_args()

def main():
    args = parse_args()
    # Tworzenie połączenia szeregowego. Zastąp 'COM_PORT' odpowiednim portem.
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    
    try:
        # Włączanie pompy nr 7
        ser.write(b'P7:ON\n')
        print("Pompa 7 została włączona.")
        
        # Czekanie przez określony czas
        time.sleep(args.time)
        
        # Wyłączanie pompy nr 7
        ser.write(b'P7:OFF\n')
        print("Pompa 7 została wyłączona.")
        
        # Odczytywanie odpowiedzi z Pico
        while ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print(line)
    
    finally:
        ser.close()

if __name__ == '__main__':
    main()

