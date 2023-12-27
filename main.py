from flask import Flask, request, render_template, jsonify, send_file
from pytube import YouTube
from moviepy.editor import *
import webbrowser
import threading

app = Flask(__name__)

# Render the upload form and YouTube link input
@app.route('/')
def upload_file():
    return render_template('upload.html')

# Function to download YouTube video
def download_video(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        video.download(filename='temp_video')
        return 'temp_video.mp4'
    except Exception as e:
        print("Error:", e)
        return None

# Function to convert video to audio in the specified format
def convert_to_audio(video_file, audio_format='mp3'):
    try:
        audio = AudioFileClip(video_file)
        duration = audio.duration
        for i, chunk in enumerate(audio.iter_chunks(chunk_duration=1)):
            # Simulate the conversion progress
            progress = int((i / (duration / 1)) * 100)
            yield f"data:{progress}\n\n"
        audio.write_audiofile(f'output_audio.{audio_format}')
        audio.close()
        yield "data:100\n\n"
    except Exception as e:
        print("Error:", e)
        yield "data:Error\n\n"

# Handle file upload and conversion
@app.route('/uploader', methods=['POST'])
def upload_file_handler():
    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            if f.filename != '':
                file_path = f.filename
                f.save(file_path)
                
                # Process the uploaded file (DWP or other format)
                audio_file = convert_to_audio(file_path, 'mp3')  # Change 'mp3' to the desired audio format
                
                if audio_file:
                    return f"Audio successfully converted to {audio_file}"
                else:
                    return "Conversion failed"
            else:
                return "No file selected"
        elif 'youtube_link' in request.form:
            youtube_link = request.form['youtube_link']
            
            # Download the YouTube video and convert to audio
            video_file = download_video(youtube_link)
            if video_file:
                return jsonify(result='/download')
            else:
                return "Download failed"

@app.route('/download')
def download():
    return send_file('output_audio.mp3', as_attachment=True)

def open_browser():
    webbrowser.open('http://localhost/')

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True)
