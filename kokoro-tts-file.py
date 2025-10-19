import asyncio
import soundfile as sf
import numpy as np  # For audio data manipulation
import argparse     # For command-line arguments
import os           # For path manipulation and file checks
import sys          # For exiting the script
import subprocess   # For calling ffmpeg
import onnxruntime  # <--- NEW: Required for ONNX session
import time         # <--- NEW: For timing generation

from kokoro_onnx import SAMPLE_RATE, Kokoro

# --- Model/Voice File Definitions ---
# Use the correct, optimized model files
MODEL_PATH = "kokoro-v1.0.int8.onnx"
VOICES_PATH = "voices-v1.0.bin"

# --- List of Valid Voices ---
# Note: I added the missing voices from your output list to the original list.
VALID_VOICES = [
    'af_alloy', 'af_aoede', 'af_bella', 'af_heart', 'af_jessica', 'af_kore',
    'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky', 'am_adam',
    'am_echo', 'am_eric', 'am_fenrir', 'am_liam', 'am_michael', 'am_onyx',
    'am_puck', 'am_santa', 'bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily',
    'bm_daniel', 'bm_fable', 'bm_george', 'bm_lewis', 
    'ef_dora', 'em_alex', 'em_santa', 'ff_siwis', 
    'hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi', 
    'if_sara', 'im_nicola', 
    'jf_alpha', 'jf_gongitsune', 'jf_nezumi', 'jf_tebukuro', 'jm_kumo', 
    'pf_dora', 'pm_alex', 'pm_santa', 
    'zf_xiaobei', 'zf_xiaoni', 'zf_xiaoxiao', 'zf_xiaoyi', 'zm_yunjian', 
    'zm_yunxi', 'zm_yunxia', 'zm_yunyang' # <--- Added missing Chinese voices
]
DEFAULT_VOICE = "af_nicole"

async def main(input_text, voice_name, output_m4a_path):
    # --- Kokoro Initialization ---
    # Check for model files first
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VOICES_PATH):
        print(f"Error: Model files not found. Please download '{MODEL_PATH}' and '{VOICES_PATH}'")
        sys.exit(1)

    print(f"Loading ONNX session for: {MODEL_PATH}")
    # Initialize the ONNX session explicitly for CPU
    session = onnxruntime.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"]) 

    # Initialize Kokoro using the session and voice weights
    kokoro = Kokoro.from_session(session, VOICES_PATH) # <--- FIXED: Use from_session
    print("Engine initialized successfully.")
    
    # --- Generate Speech ---
    print(f"Generating speech with voice: {voice_name}...")
    start_time = time.time()
    
    stream = kokoro.create_stream(
        input_text,
        voice=voice_name,
        speed=1.0,
        lang="en-us", # Assuming English, adjust if needed
    )

    # --- Collect Audio Chunks ---
    all_samples_list = []
    count = 0
    async for samples, _ in stream:
        count += 1
        # In a real app, you would send this chunk to the output immediately
        # print(f"Received chunk {count}...") 
        all_samples_list.append(samples)
    
    end_time = time.time()
    print(f"Streaming complete. Generated in {end_time - start_time:.2f} seconds across {count} chunks.")

    if not all_samples_list:
        print("Error: No audio data received from Kokoro stream.")
        sys.exit(1)

    # --- Concatenate and Convert Audio Data ---
    print("Concatenating audio chunks...")
    concatenated_samples = np.concatenate(all_samples_list)

    # Convert float samples (-1.0 to 1.0) to 16-bit PCM for ffmpeg
    print("Converting audio data format...")
    pcm_s16le = (concatenated_samples * 32767).astype(np.int16)

    # --- Convert to M4A using ffmpeg ---
    print(f"Starting FFmpeg conversion to: {output_m4a_path}")
    ffmpeg_command = [
        'ffmpeg',
        '-f', 's16le',             # Input format: signed 16-bit little-endian PCM
        '-ar', str(SAMPLE_RATE),   # Input sample rate
        '-ac', '1',                # Input channels (mono)
        '-i', 'pipe:0',            # Read PCM data from stdin
        '-c:a', 'aac',             # Output codec: AAC (standard for M4A)
        '-b:a', '128k',            # Bitrate for AAC (optional, but good practice)
        '-vn',                     # No video output
        '-y',                      # Overwrite output file if it exists
        output_m4a_path
    ]

    try:
        process = subprocess.run(
            ffmpeg_command,
            input=pcm_s16le.tobytes(), # Pass PCM data to ffmpeg's stdin
            check=True,                # Raise error if ffmpeg fails
            capture_output=True        # Capture stdout/stderr
        )
        print("FFmpeg conversion successful.")
    except FileNotFoundError:
        print("\nError: 'ffmpeg' command not found.")
        print("Please ensure ffmpeg is installed and in your system's PATH (e.g., sudo apt install ffmpeg).")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nError during ffmpeg conversion (return code {e.returncode}):")
        print(e.stderr.decode())
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate speech from a text file using Kokoro TTS and save as M4A.")
    parser.add_argument("input_file", help="Path to the input text file.")
    parser.add_argument(
        "voice",
        nargs='?', # Makes the argument optional
        default=DEFAULT_VOICE,
        help=f"Voice name to use (default: {DEFAULT_VOICE})."
    )

    args = parser.parse_args()

    # --- Read Input Text ---
    # Read text file content and perform initial checks
    # ... (File and Voice Validation remains the same) ...
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    if args.voice not in VALID_VOICES:
        print(f"Error: Invalid voice name '{args.voice}'.")
        print("Available voices are:")
        for v in VALID_VOICES:
            print(f"- {v}")
        sys.exit(1)

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        if not text_content.strip():
            print(f"Error: Input file '{args.input_file}' is empty.")
            sys.exit(1)
    except Exception as e:
        print(f"Error reading input file '{args.input_file}': {e}")
        sys.exit(1)


    # --- Determine Output Filename ---
    base_name, _ = os.path.splitext(args.input_file)
    output_path = f"{base_name}_{args.voice}.m4a"

    # --- Run Main Function ---
    print(f"Input file: {args.input_file}")
    print(f"Output file: {output_path}")
    asyncio.run(main(text_content, args.voice, output_path))

    print("Script finished.")
