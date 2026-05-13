# denoizer
# pip install dfnet soundfile
import torch
import soundfile as sf
from df.enhance import enhance, init_model, load_audio, save_audio

def enhance_arabic_voice(input_file, output_file):
    print(f"Loading model and audio: {input_file}...")
    
    # 1. Load the pre-trained DeepFilterNet model
    # This model is specifically designed for noise reduction and dereverb
    model, df_state, _ = init_model()
    
    # 2. Load your audio file
    # The library automatically handles resampling to 48kHz (required by the model)
    audio, _ = load_audio(input_file, sr=df_state.sr())
    
    print("Enhancing audio (removing noise and echo)...")
    
    # 3. Run enhancement
    # This process targets background noise and room reflections (echo/far-away sound)
    enhanced_audio = enhance(model, df_state, audio)
    
    # 4. Save the result
    save_audio(output_file, enhanced_audio, df_state.sr())
    print(f"Success! Enhanced file saved as: {output_file}")

if __name__ == "__main__":
    # Change these to your actual filenames
    input_path = r"C:\Users\hdoghmen\Downloads\d70\noizy__05.mp3"
    output_path = r"C:\Users\hdoghmen\Downloads\d70\clean__05.mp3"
    
    enhance_arabic_voice(input_path, output_path)