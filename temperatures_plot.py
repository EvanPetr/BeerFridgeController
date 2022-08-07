import math
import matplotlib.pyplot as plt

with open("temperatures_recording_1.txt") as f:
    f_buffer = f.readlines()

f_buffer = [line.replace('\x00', '') for line in f_buffer]

samples = [*range(len(f_buffer))]
temperatures = [float(item.split(",")[0]) for item in f_buffer]
offsets = [float(item.split(",")[1]) for item in f_buffer]
desired_temperatures = [float(item.split(",")[2]) for item in f_buffer]
fridge_states = [int(item.split(",")[3].strip()) for item in f_buffer]
print("ready")


plt.plot(samples, temperatures, 'r') # plotting t, a separately
plt.plot(samples, desired_temperatures, 'b') # plotting t, b separately
plt.plot(samples, fridge_states, 'g') # plotting t, c separately
plt.show()
