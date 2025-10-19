That's an astute question\! I was a bit vague in the previous response. The output I provided *is* already formatted using **Markdown**.

You can directly copy the text below and save it as your `README.md` file in your repository. It includes all the headings, lists, code blocks, and bold formatting you'd expect in a high-quality README.

-----

# 🗣️ Kokoro ONNX Text-to-Speech (CPU Focus)

An asynchronous Python wrapper for the powerful, small **Kokoro-82M TTS model** utilizing the ONNX Runtime for efficient CPU-based speech generation on Linux systems.

This project focuses on a stable, high-performance CPU setup, making it ideal for self-hosted applications, scripts, and open-source contributions.

-----

## 🚀 Quick Start (Linux)

These instructions assume you have **Python $3.10+$** and **`ffmpeg`** installed on a Debian/Ubuntu-based system (like Linux Mint).

### 1\. Setup Environment

It is **highly recommended** to use a Python virtual environment (`venv`) to isolate dependencies.

```bash
# 1. Install venv and ffmpeg utility (if needed)
sudo apt update
sudo apt install python3-venv ffmpeg

# 2. Create and enter your project directory
mkdir kokoro-tts-project
cd kokoro-tts-project

# 3. Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

### 2\. Install Dependencies

This project uses a minimal set of dependencies required for CPU execution, as listed in `requirements.txt`.

```bash
# Install the required Python packages
pip install -r requirements.txt
```

### 3\. Download Model and Voice Binaries

The repository does **not** include the large model files. Download the optimized **8-bit quantized ONNX model** and the voice weights into your project directory for the best CPU performance.

```bash
# Download the optimized quantized model (~88 MB)
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx

# Download the voice weight binaries (~27 MB)
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

-----

## 💻 Usage

### A. Simple Generation (`generate_tts_cpu.py`)

This script is a basic demonstration of single-text generation, saving the output to a `.wav` file.

```bash
python3 generate_tts_cpu.py
# Output: onnx_cpu_output.wav
```

### B. File Processing and M4A Output (`kokoro_tts_file.py`)

This script leverages **asyncio** to stream the generated audio and uses **ffmpeg** to encode the final output to the space-efficient `.m4a` format.

1.  **Create an input text file** (e.g., `/tmp/my_long_text.txt`).

2.  **Run the script:**
    The script takes the input file path as the first argument, and an optional voice name as the second.

    ```bash
    # Usage: python3 kokoro_tts_file.py <input_file> [voice_name]

    # Example using the default voice (af_nicole)
    python3 kokoro_tts_file.py /tmp/my_long_text.txt

    # Example using a different voice
    python3 kokoro_tts_file.py /tmp/my_long_text.txt am_michael
    ```

    The output file will be named based on the input: `/tmp/my_long_text_am_michael.m4a`.

### C. Listing Available Voices (`list_voices.py`)

Use this script to see all $54$ available voices, which can be used as the optional second argument to `kokoro_tts_file.py`.

```bash
python3 list_voices.py
```

-----

## 🛠️ Project Structure

| File/Folder | Purpose |
| :--- | :--- |
| **`.venv/`** | **(IGNORED)** The isolated Python virtual environment. |
| **`requirements.txt`** | Lists all required Python packages (e.g., `kokoro-onnx`, `onnxruntime`). |
| `generate_tts_cpu.py` | Simple, synchronous TTS example. |
| `list_voices.py` | Utility script to display available voices. |
| `kokoro_tts_file.py` | **Advanced:** Asynchronous streaming TTS with M4A output via `ffmpeg`. |
| `kokoro-v1.0.int8.onnx` | **(IGNORED)** The optimized 8-bit ONNX model binary. |
| `voices-v1.0.bin` | **(IGNORED)** The voice weights binary. |
| `.gitignore` | Ensures the model binaries and the `.venv` are not committed to Git. |
