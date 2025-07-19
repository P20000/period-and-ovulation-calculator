import customtkinter as ctk
from tkinter import messagebox # messagebox still works with CustomTkinter
import datetime
import json
import os

# Define the data file name
DATA_FILE = 'girlfriend_data.json'

class PeriodCalculatorApp(ctk.CTk): # Inherit from CTk instead of tk.Tk
    def __init__(self):
        super().__init__() # Call the constructor of the parent class (CTk)

        self.title("Period & Ovulation Calculator")
        self.geometry("800x700") # Set initial window size
        self.resizable(True, True) # Allow window resizing

        # --- Apply CustomTkinter Theme ---
        ctk.set_appearance_mode("light")  # Modes: "System" (default), "Light", "Dark"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

        # Custom colors to approximate the purple/blue theme from the image
        self.purple_color = "#6a0dad"
        self.darker_purple_color = "#8a2be2"
        self.light_blue_bg = "#e0f2f7"
        self.text_color = "#333333"

        # Configure CustomTkinter widgets to use desired colors and fonts
        # Note: CustomTkinter styling is more direct via widget arguments
        # rather than a global style object like ttk.Style.

        # Create a main frame to contain all other widgets
        self.main_frame = ctk.CTkFrame(self, fg_color=self.light_blue_bg, corner_radius=10) # Use fg_color for background
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20) # Add padding to main frame

        # Configure grid for responsiveness within the main_frame
        self.main_frame.grid_rowconfigure(0, weight=0) # Profile frame fixed size
        self.main_frame.grid_rowconfigure(1, weight=0) # Input frame fixed size
        self.main_frame.grid_rowconfigure(2, weight=1) # Results section can expand more
        self.main_frame.grid_columnconfigure(0, weight=1) # Column 0 expands horizontally

        self.profiles_data = self.load_data()
        self.current_profile_name = None
        self.current_profile_data = None

        # --- Profile Management Frame ---
        # Using CTkFrame with a CTkLabel as title
        self.profile_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10)
        self.profile_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.profile_frame.grid_columnconfigure(0, weight=1)
        self.profile_frame.grid_columnconfigure(1, weight=1)
        self.profile_frame.grid_columnconfigure(2, weight=1)
        self.profile_frame.grid_columnconfigure(3, weight=1)
        self.profile_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(self.profile_frame, text="Manage Profiles", font=("Arial", 14, "bold"), text_color=self.text_color).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10), padx=5)

        ctk.CTkLabel(self.profile_frame, text="Select Profile:", text_color=self.text_color).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.profile_selector = ctk.CTkComboBox(self.profile_frame, values=[], state="readonly", command=self.on_profile_select_command) # Use command for combobox
        self.profile_selector.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.load_profile_btn = ctk.CTkButton(self.profile_frame, text="Load Profile", command=self.load_selected_profile, fg_color=self.purple_color, hover_color=self.darker_purple_color)
        self.load_profile_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.new_profile_btn = ctk.CTkButton(self.profile_frame, text="New Profile", command=self.show_new_profile_input, fg_color=self.purple_color, hover_color=self.darker_purple_color)
        self.new_profile_btn.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.delete_profile_btn = ctk.CTkButton(self.profile_frame, text="Delete Profile", command=self.delete_profile, fg_color="red", hover_color="darkred")
        self.delete_profile_btn.grid(row=1, column=4, padx=5, pady=5, sticky="ew")

        self.new_profile_label = ctk.CTkLabel(self.profile_frame, text="New Profile Name:", text_color=self.text_color)
        self.new_profile_entry = ctk.CTkEntry(self.profile_frame, placeholder_text="Enter new profile name")
        self.create_profile_btn = ctk.CTkButton(self.profile_frame, text="Create Profile", command=self.create_profile, fg_color="green", hover_color="darkgreen")

        self.current_user_id_label = ctk.CTkLabel(self.profile_frame, text="Current Profile: None", text_color=self.text_color)
        self.current_user_id_label.grid(row=2, column=0, columnspan=5, sticky="w", pady=5, padx=5)


        # --- Input Section Frame ---
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(self.input_frame, text="Your Cycle Details", font=("Arial", 14, "bold"), text_color=self.text_color).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10), padx=5)

        # Row 1: Last Period Start Date
        ctk.CTkLabel(self.input_frame, text="Last Period Start Date (DD-MM-YYYY):", text_color=self.text_color).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.last_period_start_date_entry = ctk.CTkEntry(self.input_frame, placeholder_text="DD-MM-YYYY")
        self.last_period_start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Row 2: Period Duration and Cycle Length (side-by-side)
        ctk.CTkLabel(self.input_frame, text="Period Duration (days):", text_color=self.text_color).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.period_duration_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g., 5")
        self.period_duration_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.input_frame, text="Cycle Length (days):", text_color=self.text_color).grid(row=2, column=2, sticky="w", pady=5, padx=5)
        self.cycle_length_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g., 28")
        self.cycle_length_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        self.calculate_btn = ctk.CTkButton(self.input_frame, text="Get Current Mood", command=self.calculate_and_predict, fg_color=self.purple_color, hover_color=self.darker_purple_color)
        self.calculate_btn.grid(row=3, column=0, columnspan=4, pady=20)


        # --- Results Section Frame ---
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10)
        self.results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.results_frame, text="Current Mood Prediction", font=("Arial", 14, "bold"), text_color=self.text_color).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10), padx=5)

        # CTkTextbox handles its own scrollbar, no need for separate CTkScrollbar
        self.results_text = ctk.CTkTextbox(self.results_frame, wrap="word", height=100, font=("Arial", 10), text_color=self.text_color)
        self.results_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.results_text.configure(state="disabled") # Make it read-only

        # IMPORTANT: Call load_profile_names AFTER all widgets are initialized
        self.load_profile_names()

    def load_data(self):
        """
        Loads user profiles from the JSON data file.
        Includes error handling for file not found or invalid JSON.
        """
        if not os.path.exists(DATA_FILE):
            return {"profiles": {}}
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Convert date strings back to date objects from ISO format
                for profile_name, profile_data in data.get("profiles", {}).items():
                    if "last_period_start_date" in profile_data:
                        profile_data["last_period_start_date"] = datetime.date.fromisoformat(profile_data["last_period_start_date"])
                return data
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Error reading {DATA_FILE}. It might be corrupted. Starting with empty data.")
            return {"profiles": {}}
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading data: {e}")
            return {"profiles": {}}

    def save_data(self):
        """
        Saves user profiles to the JSON data file.
        Converts date objects to ISO format strings for JSON storage.
        Includes error handling for file write issues.
        """
        # Create a deep copy to modify dates for saving without altering original objects
        data_to_save = {"profiles": {}}
        for profile_name, profile_data in self.profiles_data.get("profiles", {}).items():
            profile_copy = profile_data.copy()
            if "last_period_start_date" in profile_copy:
                profile_copy["last_period_start_date"] = profile_copy["last_period_start_date"].isoformat()
            data_to_save["profiles"][profile_name] = profile_copy

        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except IOError as e:
            messagebox.showerror("Save Error", f"Could not save data to {DATA_FILE}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while saving data: {e}")

    def load_profile_names(self):
        """
        Populates the profile selector combobox.
        Attempts to load the first profile if available, or prompts for a new one.
        """
        profile_names = list(self.profiles_data.get("profiles", {}).keys())
        self.profile_selector.configure(values=profile_names) # Use configure to update values
        if profile_names:
            self.profile_selector.set(profile_names[0]) # Set the currently selected value
            self.load_selected_profile() # Load the first profile automatically
        else:
            self.profile_selector.set("") # Clear selection if no profiles
            self.update_ui_with_profile_data() # Clears input fields
            self.current_user_id_label.configure(text="Current Profile: None (Create New)")
            self.show_new_profile_input()

    def on_profile_select_command(self, choice):
        """
        Handles selection change in the profile combobox.
        CustomTkinter combobox uses a command callback with the selected value.
        """
        selected_name = choice # The selected value is passed as an argument
        if selected_name:
            self.current_profile_name = selected_name
            self.current_profile_data = self.profiles_data["profiles"][selected_name]
            self.update_ui_with_profile_data()
            self.current_user_id_label.configure(text=f"Current Profile: {self.current_profile_name}")

    def load_selected_profile(self):
        """
        Loads the currently selected profile's data into the input fields.
        """
        selected_name = self.profile_selector.get()
        if selected_name and selected_name in self.profiles_data.get("profiles", {}):
            self.current_profile_name = selected_name
            self.current_profile_data = self.profiles_data["profiles"][selected_name]
            self.update_ui_with_profile_data()
            self.current_user_id_label.configure(text=f"Current Profile: {self.current_profile_name}")
            self.hide_new_profile_input()
        elif not selected_name:
            messagebox.showinfo("Info", "Please select a profile first.")
        else:
            messagebox.showerror("Error", "Selected profile not found.")

    def update_ui_with_profile_data(self):
        """
        Updates the input fields with data from the current profile.
        Ensures entries are cleared before inserting new data.
        """
        self.last_period_start_date_entry.delete(0, ctk.END)
        self.period_duration_entry.delete(0, ctk.END)
        self.cycle_length_entry.delete(0, ctk.END)

        if self.current_profile_data:
            self.last_period_start_date_entry.insert(0, self.current_profile_data["last_period_start_date"].strftime("%d-%m-%Y"))
            self.period_duration_entry.insert(0, str(self.current_profile_data["period_duration"]))
            self.cycle_length_entry.insert(0, str(self.current_profile_data["cycle_length"]))

    def show_new_profile_input(self):
        """
        Shows the input fields for creating a new profile.
        Clears existing input fields and sets focus.
        """
        self.new_profile_label.grid(row=3, column=0, sticky="w", pady=5, padx=5) # Adjusted row
        self.new_profile_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew") # Adjusted row
        self.create_profile_btn.grid(row=3, column=3, padx=5, pady=5, sticky="ew") # Adjusted row
        self.new_profile_entry.delete(0, ctk.END)
        self.new_profile_entry.focus_set()

        self.last_period_start_date_entry.delete(0, ctk.END)
        self.period_duration_entry.delete(0, ctk.END)
        self.cycle_length_entry.delete(0, ctk.END)
        self.current_profile_name = None
        self.current_profile_data = None
        self.current_user_id_label.configure(text="Current Profile: None (Creating New)")


    def hide_new_profile_input(self):
        """Hides the input fields for creating a new profile."""
        self.new_profile_label.grid_forget()
        self.new_profile_entry.grid_forget()
        self.create_profile_btn.grid_forget()

    def create_profile(self):
        """
        Creates a new profile and saves it to the JSON file.
        Includes input validation and error handling.
        """
        profile_name = self.new_profile_entry.get().strip()
        if not profile_name:
            messagebox.showerror("Error", "Profile name cannot be empty.")
            return
        if profile_name in self.profiles_data.get("profiles", {}):
            messagebox.showerror("Error", "A profile with this name already exists. Please choose a different name.")
            return

        try:
            last_period_start_date_str = self.last_period_start_date_entry.get()
            last_period_start_date = datetime.datetime.strptime(last_period_start_date_str, "%d-%m-%Y").date()
            period_duration = int(self.period_duration_entry.get())
            cycle_length = int(self.cycle_length_entry.get())

            if period_duration <= 0 or cycle_length <= 0:
                messagebox.showerror("Input Error", "Period duration and cycle length must be positive numbers.")
                return

            if cycle_length < period_duration:
                messagebox.showwarning("Warning", "Your cycle length is shorter than your period duration. Please double-check your inputs.")

            new_profile_data = {
                "name": profile_name,
                "last_period_start_date": last_period_start_date,
                "period_duration": period_duration,
                "cycle_length": cycle_length
            }
            if "profiles" not in self.profiles_data:
                self.profiles_data["profiles"] = {}
            self.profiles_data["profiles"][profile_name] = new_profile_data
            self.save_data()
            messagebox.showinfo("Success", f"Profile '{profile_name}' created and saved!")
            self.current_profile_name = profile_name
            self.current_profile_data = new_profile_data
            self.load_profile_names()
            self.profile_selector.set(profile_name)
            self.hide_new_profile_input()
            self.current_user_id_label.configure(text=f"Current Profile: {self.current_profile_name}")
            self.update_ui_with_profile_data()

        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all fields are correctly filled. Date format: DD-MM-YYYY, Duration/Length: numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def delete_profile(self):
        """
        Deletes the currently selected profile.
        Asks for confirmation before deletion.
        """
        if not self.current_profile_name:
            messagebox.showinfo("Info", "No profile selected to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the profile '{self.current_profile_name}'?\nThis action cannot be undone."
        )

        if confirm:
            try:
                del self.profiles_data["profiles"][self.current_profile_name]
                self.save_data()
                messagebox.showinfo("Success", f"Profile '{self.current_profile_name}' deleted successfully.")

                self.current_profile_name = None
                self.current_profile_data = None
                self.update_ui_with_profile_data()
                self.results_text.configure(state="normal")
                self.results_text.delete("1.0", ctk.END)
                self.results_text.configure(state="disabled")
                self.current_user_id_label.configure(text="Current Profile: None")

                self.load_profile_names()
                if not self.profile_selector.cget("values"): # Check if values list is empty
                    self.show_new_profile_input()

            except KeyError:
                messagebox.showerror("Error", "Selected profile not found in data. It might have been deleted externally.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during profile deletion: {e}")


    def calculate_and_predict(self):
        """
        Calculates and displays the current mood based on the cycle stage.
        """
        try:
            last_period_start_date_str = self.last_period_start_date_entry.get()
            last_period_start_date = datetime.datetime.strptime(last_period_start_date_str, "%d-%m-%Y").date()
            period_duration = int(self.period_duration_entry.get())
            cycle_length = int(self.cycle_length_entry.get())

            if period_duration <= 0 or cycle_length <= 0:
                messagebox.showerror("Input Error", "Period duration and cycle length must be positive numbers.")
                return

            if cycle_length < period_duration:
                messagebox.showwarning("Warning", "Your cycle length is shorter than your period duration. Please double-check your inputs.")

            if self.current_profile_name:
                self.current_profile_data["last_period_start_date"] = last_period_start_date
                self.current_profile_data["period_duration"] = period_duration
                self.current_profile_data["cycle_length"] = cycle_length
                self.profiles_data["profiles"][self.current_profile_name] = self.current_profile_data
                self.save_data()
                messagebox.showinfo("Profile Updated", f"Profile '{self.current_profile_name}' updated successfully!")
            else:
                messagebox.showwarning("No Profile Selected", "Please create or load a profile to save these details.")
                return

            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", ctk.END)

            results_output = "--- Current Mood Prediction ---\n"
            mood = self.predict_current_mood(last_period_start_date, period_duration, cycle_length)
            results_output += mood

            self.results_text.insert("1.0", results_output) # Insert at the beginning
            self.results_text.configure(state="disabled")

        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all fields are correctly filled. Date format: DD-MM-YYYY, Duration/Length: numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during calculation: {e}")

    def predict_current_mood(self, last_period_start, period_duration, cycle_length):
        """
        Predicts the current mood based on the cycle phase for today's date.
        """
        today = datetime.date.today()
        days_since_last_period = (today - last_period_start).days

        if days_since_last_period < 0:
            return "The current date is before the recorded last period start. Cannot predict mood accurately."

        current_day_in_cycle = (days_since_last_period % cycle_length) + 1

        mood_output = f"Today ({today.strftime('%d-%m-%Y')}) is Day {current_day_in_cycle} of the cycle.\n"

        # Mood predictions based on typical cycle phases
        if 1 <= current_day_in_cycle <= period_duration:
            mood_output += "Phase: Early Follicular (Period)\nMood: Feeling tired, possibly irritable, focusing on self-care."
        elif period_duration < current_day_in_cycle <= (cycle_length - 17):
            mood_output += "Phase: Mid-Follicular\nMood: Energized, positive, and ready for new challenges."
        elif (cycle_length - 16) <= current_day_in_cycle <= (cycle_length - 12):
            mood_output += "Phase: Ovulation Window\nMood: Peak energy, confident, and highly fertile."
        elif (cycle_length - 11) <= current_day_in_cycle <= (cycle_length - 5):
            mood_output += "Phase: Early Luteal\nMood: Calm, reflective, and productive."
        elif (cycle_length - 4) <= current_day_in_cycle <= cycle_length:
            mood_output += "Phase: Late Luteal (PMS)\nMood: May experience PMS symptoms like mood swings, irritability, or fatigue. Prioritize self-care."
        else:
            mood_output += "Mood prediction not available for this cycle day. (This is an unexpected state, please check inputs)."
        return mood_output

# Run the application
if __name__ == "__main__":
    app = PeriodCalculatorApp()
    app.mainloop()
