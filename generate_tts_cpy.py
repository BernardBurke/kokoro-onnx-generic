import onnxruntime
from kokoro_onnx import Kokoro
import soundfile as sf
import time
import os

# --- 1. Settings ---
text_to_say = "This is a new test. We are using the CPU to ensure maximum compatibility on Linux Mint."
output_filename = "/tmp/onnx_cpu_output.wav"


# Model files in the same folder
model_path = "kokoro-v1.0.int8.onnx"   # <--- CHANGED TO QUANTIZED MODEL
voices_path = "voices-v1.0.bin"

# This explicitly sets ONNX Runtime to only use the CPU Execution Provider
# Note: You can also just omit the 'providers' argument, as CPU is the default fallback.
providers = ["CPUExecutionProvider"]

# --- 2. Initialize ---
# Check for model files first for cleaner errors
if not os.path.exists(model_path) or not os.path.exists(voices_path):
    print(f"ERROR: Model files not found. Please download '{model_path}' and '{voices_path}'")
    print("Execution aborted.")
    exit(1)

print(f"Loading ONNX session for: {model_path}")
print(f"Using providers: {providers}")
# Initialize the session, using only the CPU provider
session = onnxruntime.InferenceSession(model_path, providers=providers)

print(f"Loading Kokoro engine with voices from: {voices_path}")
kokoro = Kokoro.from_session(session, voices_path)

print("Engine initialized successfully.")

# --- 3. Generate Speech ---
print(f"Generating speech for: '{text_to_say}'")
start_time = time.time()

# The method is .create()
samples, sample_rate = kokoro.create(
    text=text_to_say,
    voice="af_sarah"
)

end_time = time.time()
print(f"Speech generated in {end_time - start_time:.2f} seconds.")

# --- 4. Save the Audio ---
sf.write(output_filename, samples, sample_rate)
print(f"Test complete. Audio saved to '{output_filename}'.")
