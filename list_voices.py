import onnxruntime
from kokoro_onnx import Kokoro
import os

# --- 1. Settings ---
# Use the highly efficient quantized model file
model_filename = "kokoro-v1.0.int8.onnx"
voices_filename = "voices-v1.0.bin"

# Assumes models are in the same folder as the script (current directory)
# Using direct filenames is cleaner when the directory is "."
model_path = model_filename
voices_path = voices_filename

# --- 2. Initialize ---
# Check for model files first for cleaner errors
if not os.path.exists(model_path) or not os.path.exists(voices_path):
    print(f"ERROR: Model files not found. Please download '{model_path}' and '{voices_path}'")
    print("Execution aborted.")
    exit(1)

# Use CPU provider for just listing voices, which is fast and reliable
providers = ["CPUExecutionProvider"]
print(f"Loading ONNX session for: {model_path}")
print(f"Using provider: {providers[0]}")

session = onnxruntime.InferenceSession(model_path, providers=providers)
kokoro = Kokoro.from_session(session, voices_path)

# --- 3. List Voices ---
print("\n--- Available Voices in kokoro-onnx ---")

# The kokoro.voices attribute is a dictionary; we iterate over the keys (voice names)
# We can also display the total count.
voice_list = list(kokoro.voices.keys())

for voice_name in voice_list:
    print(f"- {voice_name}")

print(f"\nTotal voices found: {len(voice_list)}")
