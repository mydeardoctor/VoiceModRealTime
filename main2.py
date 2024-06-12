import matplotlib.pyplot as plt

x_list = []
signal_list = []
sine_list = []
modulated_list = []

x = 0
s = 1
with open("text.txt", "r") as f:
    while line := f.readline():
        input_float: float = float(line)
        if s == 1:
            x_list.append(x)
            signal_list.append(input_float)
            s = 2
        elif s == 2:
            sine_list.append(input_float)
            s = 3
        else:
            x = x + 1
            modulated_list.append(input_float)
            s = 1
            
print(len(x_list), len(signal_list), len(sine_list), len(modulated_list))
plt.plot(x_list[:], signal_list[:], x_list[:], sine_list[:], x_list[:], modulated_list[:])
plt.show()