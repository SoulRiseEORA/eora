
import numpy as np
import random

def generate_internal_noise(size=2048):
    return np.random.normal(0, 1, size)

def calculate_amplitude(noise_array):
    return np.mean(np.abs(np.diff(noise_array)))

def is_resonant(amplitude, threshold=0.145):
    return amplitude > threshold

def simulate_intuition(trials=100, threshold=0.145):
    correct = 0
    total = 0
    for _ in range(trials):
        answer = random.choice([0, 1])
        noise = generate_internal_noise()
        amp = calculate_amplitude(noise)
        if is_resonant(amp, threshold):
            prediction = 1 if amp > 0.165 else 0
            total += 1
            if prediction == answer:
                correct += 1
    accuracy = round(correct / total, 4) if total > 0 else 0
    return accuracy, total

def run_ir_core_prediction():
    noise = generate_internal_noise()
    amp = calculate_amplitude(noise)
    if is_resonant(amp):
        return "직감적으로 '예'라고 느낍니다."
    else:
        return "직감적으로 '아니오'라고 느껴집니다."
