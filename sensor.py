import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
import socket

# Set up GPIO:
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

# Set up DHT sensor:
dht_device = adafruit_dht.DHT11(board.D4)  # using board.D4 for GPIO4

def client_program():
    host = '192.168.137.228'  # Laptop's IP address
    port = 12345  # the same port as used by the server

    # Instantiate and connect socket:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            print("Connected to server successfully.")
        
            while True:
                try:
                    # Read the temperature and humidity
                    temperature = dht_device.temperature
                    humidity = dht_device.humidity
                    if temperature is not None and humidity is not None:
                        print(f"Temp: {temperature:.1f} C    Humidity: {humidity}%")
                        data = f'Temperature: {temperature} C\n'
                        client_socket.sendall(data.encode())
                        data= f'Humidity: {humidity}%\n'
                        client_socket.sendall(data.encode())
                    else:
                        print('Failed to get reading from DHT sensor. Try again!')
                    
                    # Check air quality:
                    if GPIO.input(17):
                        print("Harmful gases detected!")
                        client_socket.sendall("Harmful gases detected!\n".encode())
                    else:
                        print("Air quality is normal.")
                        client_socket.sendall("Air quality is normal.\n".encode())
                    
                    time.sleep(2)  # Adjust sleep time as necessary
                except RuntimeError as e:
                    print(f"Failed to read from DHT sensor: {e}")
                except socket.error as e:
                    print(f"Socket error: {e}")
                    break  # Exit the loop if a socket error occurs

        except ConnectionRefusedError:
            print("Connection refused. Ensure the server is running and reachable.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            GPIO.cleanup()

if __name__ == '__main__':
    client_program()
