import tkinter as tk
from tkinter import font, ttk, filedialog, messagebox
from deep_translator import GoogleTranslator
import speech_recognition as sr
import pyttsx3
import threading
from PIL import Image, ImageTk

def initialize_speech_engine():
    """Initialize the text-to-speech engine."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
    return engine

def speak_text(engine, text):
    """Speak the provided text using the text-to-speech engine."""
    engine.say(text)
    engine.runAndWait()

def save_translation():
    """Save the recognized and translated text to a file."""
    recognized_text = recognized_text_area.get(1.0, tk.END).strip()
    translated_text = translated_text_area.get(1.0, tk.END).strip()
    
    if not recognized_text and not translated_text:
        messagebox.showwarning("Save Error", "There is no text to save.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write("Recognized/Text Input:\n")
            file.write(recognized_text + "\n\n")
            file.write("Translated Text:\n")
            file.write(translated_text)
        messagebox.showinfo("Save Successful", f"Translation saved to {file_path}")

def clear_text_areas():
    """Clear the recognized and translated text areas."""
    recognized_text_area.delete(1.0, tk.END)
    translated_text_area.delete(1.0, tk.END)
    status_label.config(text="")

def add_to_history(recognized_text, translated_text):
    """Add the recognized and translated text to the history listbox."""
    history_listbox.insert(tk.END, f"Original: {recognized_text}")
    history_listbox.insert(tk.END, f"Translated: {translated_text}")
    history_listbox.insert(tk.END, "-" * 40)

def recognize_and_translate():
    def task():
        recognizer = sr.Recognizer()
        engine = initialize_speech_engine()
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=microphone_sensitivity.get())
            status_label.config(text="Listening...")
            progress_bar.start()
            root.update()
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                recognized_text_area.delete(1.0, tk.END)
                recognized_text_area.insert(tk.END, text)
                
                target_language_name = language_var.get()
                target_language_code = languages[target_language_name]
                
                translated_text = GoogleTranslator(source='auto', target=target_language_code).translate(text)
                translated_text_area.delete(1.0, tk.END)
                translated_text_area.insert(tk.END, translated_text)
                
                speak_text(engine, translated_text)
                status_label.config(text="Translation completed!")
                
                add_to_history(text, translated_text)
                
            except sr.UnknownValueError:
                status_label.config(text="Sorry, could not recognize the speech.")
            
            except sr.RequestError:
                status_label.config(text="Network error: Could not reach the recognition service.")
            
            except Exception as e:
                status_label.config(text=f"An error occurred: {e}")
            
            finally:
                progress_bar.stop()

    threading.Thread(target=task).start()

def translate_text_input():
    """Translate text input manually entered by the user."""
    engine = initialize_speech_engine()
    
    text = recognized_text_area.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter text to translate.")
        return
    
    try:
        target_language_name = language_var.get()
        target_language_code = languages[target_language_name]
        
        translated_text = GoogleTranslator(source='auto', target=target_language_code).translate(text)
        translated_text_area.delete(1.0, tk.END)
        translated_text_area.insert(tk.END, translated_text)
        
        speak_text(engine, translated_text)
        status_label.config(text="Translation completed!")
        
        add_to_history(text, translated_text)
        
    except Exception as e:
        status_label.config(text=f"An error occurred: {e}")

def create_gui():
    global root, recognized_text_area, translated_text_area, language_var, status_label, languages, history_listbox, progress_bar, microphone_sensitivity

    root = tk.Tk()
    root.title("Speech Recognition and Translation")
    root.geometry("900x700")
    root.configure(bg='#2C3E50')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 12), background='#3498DB', foreground='white')
    style.configure('TCombobox', font=('Helvetica', 12))
    style.configure('TNotebook', background='#2C3E50')
    style.configure('TNotebook.Tab', font=('Helvetica', 12), padding=[10, 5], background='#34495E', foreground='white')

    custom_font = font.Font(family="Helvetica", size=12)
    large_font = font.Font(family="Helvetica", size=20, weight="bold")

    # Add a logo or banner
    try:
        logo = Image.open("logo.jpg")  # Replace with your logo file
        logo = logo.resize((200, 100), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(root, image=logo_tk, bg='#2C3E50')
        logo_label.image = logo_tk
        logo_label.pack(pady=10)
    except FileNotFoundError:
        print("Logo file not found. Skipping logo display.")

    title_label = tk.Label(root, text="Speech Recognition and Translation", font=large_font, bg='#2C3E50', fg='white')
    title_label.pack(pady=10)

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    main_frame = ttk.Frame(notebook, style='TNotebook')
    history_frame = ttk.Frame(notebook, style='TNotebook')

    notebook.add(main_frame, text="Main")
    notebook.add(history_frame, text="History")

    # Main Frame
    text_frame = tk.Frame(main_frame, bg='#2C3E50')
    text_frame.pack(pady=10)

    recognized_text_area = tk.Text(text_frame, height=5, width=30, font=custom_font, bg='#ECF0F1', fg='#2C3E50', wrap=tk.WORD)
    recognized_text_area.grid(row=0, column=0, padx=5)
    recognized_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=recognized_text_area.yview)
    recognized_scrollbar.grid(row=0, column=1, sticky='ns')
    recognized_text_area.config(yscrollcommand=recognized_scrollbar.set)

    language_var = tk.StringVar(value='French')
    languages = {
        'French': 'fr', 'Spanish': 'es', 'German': 'de', 'Chinese': 'zh-CN',
        'Japanese': 'ja', 'Russian': 'ru', 'Italian': 'it', 'Portuguese': 'pt',
        'Hindi': 'hi', 'Arabic': 'ar', 'Dutch': 'nl', 'Korean': 'ko',
        'Greek': 'el', 'Turkish': 'tr', 'Polish': 'pl', 'Swedish': 'sv',
        'Finnish': 'fi', 'Norwegian': 'no', 'Danish': 'da', 'Hebrew': 'he',
        'Thai': 'th', 'Vietnamese': 'vi'
    }
    
    language_menu = ttk.Combobox(text_frame, textvariable=language_var, values=list(languages.keys()), font=custom_font, state='readonly')
    language_menu.grid(row=0, column=2, padx=5)

    translated_text_area = tk.Text(text_frame, height=5, width=30, font=custom_font, bg='#ECF0F1', fg='#2C3E50', wrap=tk.WORD)
    translated_text_area.grid(row=0, column=3, padx=5)
    translated_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=translated_text_area.yview)
    translated_scrollbar.grid(row=0, column=4, sticky='ns')
    translated_text_area.config(yscrollcommand=translated_scrollbar.set)

    button_frame = tk.Frame(main_frame, bg='#2C3E50')
    button_frame.pack(pady=10)

    # Load and add microphone icon to the voice recognition button
    try:
        mic_icon = Image.open("voice.png")  # Replace with your microphone icon file
        mic_icon = mic_icon.resize((20, 20), Image.Resampling.LANCZOS)
        mic_icon_tk = ImageTk.PhotoImage(mic_icon)
        translate_voice_button = ttk.Button(button_frame, text=" Start Voice Recognition", image=mic_icon_tk, compound=tk.LEFT, command=recognize_and_translate)
        translate_voice_button.image = mic_icon_tk  # Keep a reference to avoid garbage collection
    except FileNotFoundError:
        translate_voice_button = ttk.Button(button_frame, text="Start Voice Recognition", command=recognize_and_translate)
        print("Microphone icon file not found. Skipping icon display.")

    translate_voice_button.grid(row=0, column=0, padx=10)

    translate_text_button = ttk.Button(button_frame, text="Translate Text Input", command=translate_text_input)
    translate_text_button.grid(row=0, column=1, padx=10)

    save_button = ttk.Button(button_frame, text="Save Translation", command=save_translation)
    save_button.grid(row=0, column=2, padx=10)

    clear_button = ttk.Button(button_frame, text="Clear", command=clear_text_areas)
    clear_button.grid(row=0, column=3, padx=10)

    status_label = tk.Label(main_frame, text="", font=custom_font, bg='#2C3E50', fg='white')
    status_label.pack(pady=5)

    # Microphone sensitivity slider
    microphone_sensitivity = tk.DoubleVar(value=1.0)
    sensitivity_label = tk.Label(main_frame, text="Microphone Sensitivity:", font=custom_font, bg='#2C3E50', fg='white')
    sensitivity_label.pack(pady=5)
    sensitivity_slider = ttk.Scale(main_frame, from_=0.5, to=5.0, orient=tk.HORIZONTAL, variable=microphone_sensitivity)
    sensitivity_slider.pack(pady=5)

    # Progress bar
    progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
    progress_bar.pack(pady=5)

    # History Frame
    history_label = tk.Label(history_frame, text="Translation History", font=large_font, bg='#2C3E50', fg='white')
    history_label.pack(pady=10)

    history_listbox = tk.Listbox(history_frame, font=custom_font, bg='#ECF0F1', fg='#2C3E50')
    history_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
