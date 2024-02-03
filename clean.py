from pydub import AudioSegment, utils
import noisereduce as nr
import os
import zipfile
from pydub.exceptions import CouldntDecodeError
import shutil
import numpy as np
import soundfile as sf

def get_audio_codec(file_path):
    try:
        info = utils.mediainfo(file_path)
        return info.get('codec_name', None)
    except Exception as e:
        print(f"Error getting codec information for {file_path}: {e}")
        return None

def reduce_noise(input_zip_path, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the zip file
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        # Extract all files to a temporary directory inside samples folder
        temp_dir = os.path.join("samples", "temp_extracted_files")
        os.makedirs(temp_dir, exist_ok=True)
        zip_ref.extractall(temp_dir)

        # Process each audio file in the temp directory
        for filename in os.listdir(temp_dir):
            if filename.endswith(".mp3"):
                input_file_path = os.path.join(temp_dir, filename)
                print(f"input_file_path: {input_file_path}")
                
				# Get the codec information
                codec = get_audio_codec(input_file_path)
                if codec is None:
                    print(f"Error getting codec information for {filename}. Skipping.")
                    continue

                print(f"Codec: {codec}")
                
                try:
                    # Load the audio file (extract audio, but this method assumes video w/ audio)
                    #also weirdly mp4 works even though the audio is actually mp3
                    audio = AudioSegment.from_file(input_file_path, format="mp4", codec="aac")
                except CouldntDecodeError:
                    print(f"Error decoding {filename}. Skipping.")
                    continue
                
				# Convert audio to numpy array
                y = np.array(audio.get_array_of_samples())
                sr = audio.frame_rate
                        
                # Perform noise reduction
                reduced_audio_array = nr.reduce_noise(y, sr)

				# Convert the numpy array back to AudioSegment
                #reduced_audio = AudioSegment.from_numpy_array(reduced_audio_array.astype(np.int16), sr)
                temp_wav_file = os.path.join(temp_dir, "temp_reduced.wav")
                sf.write(temp_wav_file, reduced_audio_array, sr)

                # Load the temporary WAV file using pydub
                reduced_audio = AudioSegment.from_file(temp_wav_file, format="wav")
                
                # Save the reduced audio to the output folder
                output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_reduced.wav")
                reduced_audio.export(output_file_path, format="wav")

        # Clean up: remove the temporary directory and its contents
        #shutil.rmtree(temp_dir)

if __name__ == "__main__":
    input_zip_file = os.path.join(".", "samples", "20 additional recordings.zip")
    output_folder = os.path.join(".", "samples", "reducedAudio")

    reduce_noise(input_zip_file, output_folder)