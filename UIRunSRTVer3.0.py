import tkinter as tk
from tkinter import filedialog
import pysrt
from datetime import datetime, timedelta

class SubtitlePlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitle Player")

        # Configure window dimensions and center it on the screen
        window_width = 1200
        window_height = 180
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = screen_height - window_height - 40 # Top of the screen
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Configure window appearance
        self.root.configure(bg='black')

        self.root.attributes("-topmost", True)  # Always on top
        self.root.overrideredirect(True)
        
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.wm_attributes("-alpha", 0.95)

        # Add a label to display the current time
        self.current_time_label = tk.Label(root, text="00:00:00", font=("Helvetica", 12), fg="white", bg="#040406")
        self.current_time_label.pack(side=tk.LEFT, pady=4)

        # Subtitle display area
        self.subtitle_label = tk.Label(root, text="", font=("Helvetica", 15), justify="center",
                                       fg="white", bg="black", relief="flat", padx=10, pady=2)
        self.subtitle_label.pack(side=tk.LEFT, expand=True)

        self.play_button = tk.Button(root, text="Play", command=self.play_subtitle , fg="white", bg="#040406")
        self.play_button.pack(side=tk.RIGHT, padx=10, pady=4)

        self.pause_button = tk.Button(root, text="Pause", command=self.pause_subtitle , fg="white", bg="#040406")
        self.pause_button["state"] = "disabled"
        self.pause_button.pack(side=tk.RIGHT, padx=10, pady=4)

        self.resume_button = tk.Button(root, text="Resume", command=self.resume_subtitle , fg="white", bg="#040406")
        self.resume_button["state"] = "disabled"
        self.resume_button.pack(side=tk.RIGHT, padx=10, pady=4)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_subtitle, fg="white", bg="#040406" )
        self.stop_button["state"] = "disabled"
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=4)

        self.next_button = tk.Button(root, text="Next", command=self.next_subtitle, fg="white", bg="#040406" )
        self.next_button["state"] = "disabled"
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=4)

        self.previous_button = tk.Button(root, text="Previous", command=self.previous_subtitle , fg="white", bg="#040406")
        self.previous_button["state"] = "disabled"
        self.previous_button.pack(side=tk.RIGHT, padx=10, pady=4)

        # Load subtitle button
        self.load_button = tk.Button(root, text="Load Subtitle", command=self.load_subtitle, fg="white", bg="#040406")
        self.load_button.pack(side=tk.RIGHT, padx=10, pady=4)

        # Initialize subtitle-related variables
        self.subtitle_file = None
        self.subtitles = []
        self.current_segment_index = 0
        self.after_id = None
        self.start_time = None
        self.pause_time = None

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def time_to_milliseconds(self, time):
        return int(time.hours * 3600000 + time.minutes * 60000 + time.seconds * 1000 + time.milliseconds)

    def load_subtitle(self):
        file_path = filedialog.askopenfilename(filetypes=[("SRT Files", "*.srt")])

        try:
            if file_path:
                self.subtitle_file = file_path
                self.subtitles = pysrt.open(file_path)
                self.play_button["state"] = "normal"
        except Exception as e:
            # Handle the exception, e.g., show an error message
            print(f"Error loading subtitle: {e}")

    def play_subtitle(self):
        if self.subtitles:
            self.play_button["state"] = "disabled"
            self.pause_button["state"] = "normal"
            self.stop_button["state"] = "normal"
            self.previous_button["state"] = "normal"
            self.next_button["state"] = "normal"
            self.start_time = datetime.now() - (self.pause_time if self.pause_time else timedelta())
            self.current_segment_index = 0
            self.play_subtitle_segment_loop()

    def play_subtitle_segment_loop(self):
        if self.current_segment_index < len(self.subtitles):
            segment = self.subtitles[self.current_segment_index]
            self.subtitle_label["text"] = segment.text

            elapsed_time = datetime.now() - self.start_time
            formatted_time = str(elapsed_time).split(".")[0]
            self.current_time_label["text"] = f"Current Time: {formatted_time}"

            current_time = elapsed_time.total_seconds()
            start_time_segment = self.time_to_milliseconds(segment.start)
            end_time_segment = self.time_to_milliseconds(segment.end)

            if start_time_segment <= current_time * 1000 <= end_time_segment:
                self.subtitle_label["text"] = segment.text
                self.subtitle_label["bg"] = "#040406"
            else:
                self.subtitle_label["text"] = ""
                self.subtitle_label["bg"] = "black"

            if self.current_segment_index == 0:
                self.previous_button["state"] = "disabled"
            else:
                self.previous_button["state"] = "normal"

            if self.current_segment_index == len(self.subtitles) - 1:
                self.next_button["state"] = "disabled"
            else:
                self.next_button["state"] = "normal"

            if current_time * 1000 >= end_time_segment:
                self.current_segment_index += 1

            self.after_id = self.root.after(200, self.play_subtitle_segment_loop)

        else:
            self.play_button["state"] = "normal"
            self.pause_button["state"] = "disabled"
            self.resume_button["state"] = "disabled"
            self.stop_button["state"] = "disabled"
            self.previous_button["state"] = "disabled"
            self.next_button["state"] = "disabled"
            self.current_segment_index = 0
            self.start_time = None

    def pause_subtitle(self):
        self.pause_button["state"] = "disabled"
        self.resume_button["state"] = "normal"
        self.stop_button["state"] = "normal"
        self.pause_time = datetime.now() - self.start_time
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def resume_subtitle(self):
        self.pause_button["state"] = "normal"
        self.resume_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        self.start_time = datetime.now() - self.pause_time
        self.play_subtitle_segment_loop()

    def stop_subtitle(self):
        self.play_button["state"] = "normal"
        self.pause_button["state"] = "disabled"
        self.resume_button["state"] = "disabled"
        self.stop_button["state"] = "disabled"
        self.previous_button["state"] = "disabled"
        self.next_button["state"] = "disabled"
        self.subtitle_label["text"] = ""
        self.subtitle_label["bg"] = "black"
        self.pause_time = None
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def previous_subtitle(self):
        if self.current_segment_index > 0:
            self.current_segment_index -= 1
            segment = self.subtitles[self.current_segment_index]

            start_time_x = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            start_time_segment_x = datetime.now().replace(
                hour=segment.start.hours,
                minute=segment.start.minutes,
                second=segment.start.seconds,
                microsecond=segment.start.milliseconds * 1000
            )

            time_count = start_time_segment_x - start_time_x

            start_time_segment_y = self.start_time + time_count

            result = datetime.now() - start_time_segment_y
            self.start_time += result

            self.root.after_cancel(self.after_id)
            self.play_subtitle_segment_loop()
        else:
            self.previous_button["state"] = "disabled"

    def next_subtitle(self):
        if self.current_segment_index < len(self.subtitles):
            self.current_segment_index += 1
            segment = self.subtitles[self.current_segment_index]

            start_time_x = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            start_time_segment_x = datetime.now().replace(
                hour=segment.start.hours,
                minute=segment.start.minutes,
                second=segment.start.seconds,
                microsecond=segment.start.milliseconds * 1000
            )

            time_count = start_time_segment_x - start_time_x

            start_time_segment_y = self.start_time + time_count

            result = start_time_segment_y - datetime.now()
            self.start_time -= result

            self.root.after_cancel(self.after_id)
            self.play_subtitle_segment_loop()
        else:
            self.next_button["state"] = "disabled"

    def run(self):
        self.root.mainloop()

    def on_closing(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    player = SubtitlePlayer(root)
    player.run()
