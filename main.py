import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import numpy as np
import threading


def extract_melody(audio_path):
    y, sr = librosa.load(audio_path)
    print("Audio loaded")
    melody, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    if isinstance(melody, tuple):
        melody = melody[0]  # Select only the first return value if a tuple is returned
    print("Melody extracted")
    return melody


def convert_to_notes(melody):
    melody = melody[~np.isnan(melody)]  # Remove NaN values
    note_names = librosa.hz_to_note(melody)
    print("Melody converted to notes")
    return note_names


def map_to_sargam(note_names):
    western_to_sargam = {
        'C': 'Sa', 'C#': 'Re', 'D': 'Re', 'D#': 'Ga', 'E': 'Ga',
        'F': 'Ma', 'F#': 'Ma', 'G': 'Pa', 'G#': 'Dha', 'A': 'Dha',
        'A#': 'Ni', 'B': 'Ni'
    }

    sargam_notes = []
    for note in note_names:
        if note:
            base_note = note[:-1]  # remove octave number
            sargam_note = western_to_sargam.get(base_note, 'Sa')
            sargam_notes.append(sargam_note)

    print("Notes mapped to sargam")
    return sargam_notes


def adjust_octaves(sargam_notes, note_names):
    adjusted_sargam = []
    for sargam_note, note_name in zip(sargam_notes, note_names):
        if note_name:
            octave = int(note_name[-1])  # get the octave number
            if octave == 4:
                adjusted_sargam.append(sargam_note)  # middle octave
            elif octave < 4:
                adjusted_sargam.append('.' + sargam_note)  # lower octave
            elif octave > 4:
                adjusted_sargam.append("'" + sargam_note)  # higher octave

    print("Octaves adjusted")
    return adjusted_sargam


def convert_and_display():
    audio_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if not audio_path:
        return

    indicator_label.config(text=f"File uploaded: {audio_path.split('/')[-1]}")
    loader_label.config(text="Processing... Please wait.")
    root.update_idletasks()

    def process_audio():
        try:
            melody = extract_melody(audio_path)
            if melody is None:
                messagebox.showerror("Error", "Failed to extract melody from the audio file.")
                loader_label.config(text="")
                return

            note_names = convert_to_notes(melody)
            sargam_notes = map_to_sargam(note_names)
            adjusted_sargam = adjust_octaves(sargam_notes, note_names)

            sargam_text = ' '.join(adjusted_sargam)
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, sargam_text)
            loader_label.config(text="")
            messagebox.showinfo("Success", "Sargam notation has been generated successfully.")
        except Exception as e:
            loader_label.config(text="")
            messagebox.showerror("Error", f"An error occurred: {e}")

    threading.Thread(target=process_audio).start()


def create_gradient_frame(frame, color1, color2):
    canvas = tk.Canvas(frame, width=400, height=400)
    canvas.pack(fill=tk.BOTH, expand=True)

    for i in range(400):
        r = int(color1[1:3], 16) + (int(color2[1:3], 16) - int(color1[1:3], 16)) * i // 400
        g = int(color1[3:5], 16) + (int(color2[3:5], 16) - int(color1[3:5], 16)) * i // 400
        b = int(color1[5:7], 16) + (int(color2[5:7], 16) - int(color1[5:7], 16)) * i // 400
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, 400, i, fill=color)

    return canvas


def create_gui():
    global root, output_text, indicator_label, loader_label

    root = tk.Tk()
    root.title("MusicTranscriber")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(padx=10, pady=10)

    gradient_canvas = create_gradient_frame(frame, "#ffccff", "#66ccff")

    title_label = tk.Label(frame, text="MusicTranscriber", font=("Arial", 18, "bold"), bg="#ffccff")
    title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

    desc_label = tk.Label(frame, text="Convert a song into bansuri flute sargam notation", font=("Arial", 12),
                          bg="#ffccff")
    desc_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    convert_button = tk.Button(frame, text="Select Audio File and Convert", command=convert_and_display,
                               font=("Arial", 12, "bold"), bg="#66ccff", fg="white")
    convert_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    indicator_label = tk.Label(frame, text="", font=("Arial", 10), bg="#ffccff", fg="green")
    indicator_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    loader_label = tk.Label(frame, text="", font=("Arial", 10), bg="#ffccff", fg="red")
    loader_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    output_text = tk.Text(frame, wrap=tk.WORD, width=50, height=10, font=("Arial", 12), bg="#e6f7ff")
    output_text.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
