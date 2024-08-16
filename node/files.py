import os
import torchaudio
from tkinter import Tk, filedialog

class Xstu_SaveAudio:
    SUPPORTED_FORMATS = ('.wav', '.mp3', '.ogg', '.flac', '.aiff', '.aif')

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", ),
                "filename": ("STRING", {"default": "output.wav", "multiline": False}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save"

    CATEGORY = "🐅Xstu/文件处理"

    def save(self, audio, filename):
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            initialfile=filename,
            filetypes=[("Audio Files", SaveAudio.SUPPORTED_FORMATS)],
            defaultextension=SaveAudio.SUPPORTED_FORMATS
        )
        if file_path:
            waveform = audio["waveform"].squeeze(0)
            sample_rate = audio["sample_rate"]
            torchaudio.save(file_path, waveform, sample_rate)
            print(f"Audio saved to {file_path}")
        else:
            print("Save operation was cancelled.")