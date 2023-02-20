import numpy as np

def acquire_L5_signal(I5, Q5, sdr_data, sample_rate, max_doppler):
    # Convert I5 and Q5 codes to complex numbers
    gold_code = I5 + 1j * Q5
    gold_code_length = len(gold_code)

    # Generate a range of Doppler shifts to search over
    doppler_shifts = np.linspace(-max_doppler, max_doppler, num=gold_code_length)

    # Initialize arrays to store the correlation results
    correlation_results = np.zeros((len(doppler_shifts), gold_code_length), dtype=complex)
    peak_values = np.zeros(len(doppler_shifts))

    # Loop over the range of Doppler shifts
    for i, doppler_shift in enumerate(doppler_shifts):
        # Apply Doppler shift to the gold code
        shifted_gold_code = gold_code * np.exp(2j * np.pi * doppler_shift * np.arange(gold_code_length) / sample_rate)

        # Correlate the raw SDR data with the shifted gold code
        correlation = np.correlate(sdr_data, shifted_gold_code, mode="same")

        # Store the correlation result
        correlation_results[i, :] = correlation

        # Store the peak of the correlation result
        peak_values[i] = np.max(np.abs(correlation))

    # Find the Doppler shift with the highest peak correlation
    best_doppler_index = np.argmax(peak_values)
    best_doppler_shift = doppler_shifts[best_doppler_index]

    # Apply the best Doppler shift to the gold code
    best_shifted_gold_code = gold_code * np.exp(2j * np.pi * best_doppler_shift * np.arange(gold_code_length) / sample_rate)

    # Correlate the raw SDR data with the best shifted gold code
    best_correlation = np.correlate(sdr_data, best_shifted_gold_code, mode="same")

    # Find the peak of the best correlation result
    best_peak_index = np.argmax(np.abs(best_correlation))

    # Extract the L5 signal from the raw SDR data
    L5_signal = sdr_data[best_peak_index : best_peak_index + gold_code_length]

    return L5_signal, best_doppler_shift
