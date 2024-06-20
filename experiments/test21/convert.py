import os
import ffmpeg

def convert_h264_to_mp4(source_folder):
    # Przechodzimy przez wszystkie pliki w folderze
    for filename in os.listdir(source_folder):
        if filename.endswith(".h264"):
            source_path = os.path.join(source_folder, filename)
            # Tworzymy nazwę dla pliku wyjściowego .mp4
            output_path = os.path.splitext(source_path)[0] + ".mp4"
            try:
                # Wykonujemy konwersję za pomocą ffmpeg
                ffmpeg.input(source_path).output(output_path).run()
                print(f'Successfully converted {filename} to {output_path}')
            except Exception as e:
                print(f'Error converting {filename}: {e}')

if __name__ == "__main__":
    # Ustawiamy folder źródłowy na aktualny katalog
    source_folder = os.getcwd()
    convert_h264_to_mp4(source_folder)

