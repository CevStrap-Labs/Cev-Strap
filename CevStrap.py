import os
import subprocess
import requests
import json
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog, colorchooser
from tkinter.scrolledtext import ScrolledText
import threading
import shutil
import time

CONFIG_FILE = os.path.join(os.getcwd(), "CustomRoblox", "cevstrap_config.json")
CUSTOM_ROBLOX_DIR = os.path.join(os.getcwd(), "CustomRoblox")
CUSTOM_ROBLOX_INSTALLER_PATH = os.path.join(CUSTOM_ROBLOX_DIR, "RobloxPlayerInstaller.exe")
CUSTOM_ROBLOX_STUDIO_PATH = os.path.join(CUSTOM_ROBLOX_DIR, "RobloxStudioLauncherBeta.exe")
FAST_FLAGS = {}
ROBLOX_COLORS = {
    "background": "#2E2E2E",
    "text": "#FFFFFF",
    "button": "#3C3F41"
}
BG_COLOR = "#2E2E2E"
FG_COLOR = "#FFFFFF"
BUTTON_COLOR = "#3C3F41"
TEXT_COLOR = "#FFFFFF"
ENTRY_COLOR = "#4B4B4B"
RUNNING_INSTANCES = {}

def get_latest_roblox_version():
    response = requests.get("https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer")
    if response.status_code == 200:
        data = response.json()
        return data["clientVersionUpload"]
    else:
        raise Exception("Failed to fetch Roblox version")

def install_roblox():
    if not os.path.exists(CUSTOM_ROBLOX_DIR):
        os.makedirs(CUSTOM_ROBLOX_DIR)
    
    installer_url = "https://setup.rbxcdn.com/RobloxPlayerInstaller.exe"
    try:
        response = requests.get(installer_url)
        with open(CUSTOM_ROBLOX_INSTALLER_PATH, "wb") as f:
            f.write(response.content)
        
        subprocess.run([CUSTOM_ROBLOX_INSTALLER_PATH, "-install", "-silent"], cwd=CUSTOM_ROBLOX_DIR, check=True)
        log("Roblox installed successfully in the CustomRoblox directory!")
    except Exception as e:
        log(f"Failed to install Roblox: {e}")

def update_fastflags(version, flags, instance_id=None):
    if instance_id:
        fast_flags_path = os.path.join(CUSTOM_ROBLOX_DIR, f"Instance_{instance_id}", "ClientSettings", "ClientAppSettings.json")
    else:
        fast_flags_path = os.path.join(CUSTOM_ROBLOX_DIR, "Versions", version, "ClientSettings", "ClientAppSettings.json")
    
    os.makedirs(os.path.dirname(fast_flags_path), exist_ok=True)
    
    with open(fast_flags_path, "w") as f:
        json.dump(flags, f, indent=4)

def launch_roblox(instance_id=None):
    global FAST_FLAGS, RUNNING_INSTANCES
    try:
        version = get_latest_roblox_version()
        
        if instance_id is not None:
            instance_dir = os.path.join(CUSTOM_ROBLOX_DIR, f"Instance_{instance_id}")
            os.makedirs(instance_dir, exist_ok=True)
            update_fastflags(version, FAST_FLAGS, instance_id)
        else:
            instance_dir = CUSTOM_ROBLOX_DIR
        
        process = subprocess.Popen([CUSTOM_ROBLOX_INSTALLER_PATH, "--app", instance_dir])
        RUNNING_INSTANCES[instance_id] = process
        log(f"Roblox launched successfully! Instance ID: {instance_id}")
    except Exception as e:
        log(f"An error occurred: {e}")

def launch_roblox_studio():
    try:
        subprocess.Popen([CUSTOM_ROBLOX_STUDIO_PATH])
        log("Roblox Studio launched successfully!")
    except Exception as e:
        log(f"Failed to launch Roblox Studio: {e}")

def stop_instance(instance_id):
    if instance_id in RUNNING_INSTANCES:
        RUNNING_INSTANCES[instance_id].terminate()
        del RUNNING_INSTANCES[instance_id]
        log(f"Stopped instance {instance_id}")
    else:
        log(f"Instance {instance_id} is not running.")

def launch_multi_instance():
    num_instances = simpledialog.askinteger("Multi-Instance", "Enter the number of instances to launch:", minvalue=1, maxvalue=10)
    if num_instances:
        for i in range(num_instances):
            threading.Thread(target=launch_roblox, args=(i + 1,)).start()
            log(f"Launched instance {i + 1}")

def add_fastflag():
    global FAST_FLAGS
    flag = simpledialog.askstring("Add FastFlag", "Enter the FastFlag name (e.g., FFlagDebugGraphicsPreferOpenGL):")
    value = simpledialog.askstring("Add FastFlag", "Enter the FastFlag value (e.g., True/False):")
    if flag and value:
        FAST_FLAGS[flag] = value
        update_fastflags_listbox()

def remove_fastflag():
    global FAST_FLAGS
    selected = fastflags_listbox.curselection()
    if selected:
        flag = fastflags_listbox.get(selected)
        del FAST_FLAGS[flag]
        update_fastflags_listbox()

def update_fastflags_listbox():
    fastflags_listbox.delete(0, tk.END)
    for flag, value in FAST_FLAGS.items():
        fastflags_listbox.insert(tk.END, f"{flag}: {value}")

def save_config():
    config = {
        "fast_flags": FAST_FLAGS,
        "roblox_colors": ROBLOX_COLORS
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    log("Configuration saved successfully!")

def load_config():
    global FAST_FLAGS, ROBLOX_COLORS
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        FAST_FLAGS = config.get("fast_flags", {})
        ROBLOX_COLORS = config.get("roblox_colors", ROBLOX_COLORS)
        update_fastflags_listbox()
        log("Configuration loaded successfully!")
    else:
        log("No configuration file found.")

def log(message):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, message + "\n")
    log_area.config(state=tk.DISABLED)
    log_area.yview(tk.END)

def customize_roblox_colors():
    global ROBLOX_COLORS
    background_color = colorchooser.askcolor(title="Choose Background Color", color=ROBLOX_COLORS["background"])[1]
    text_color = colorchooser.askcolor(title="Choose Text Color", color=ROBLOX_COLORS["text"])[1]
    button_color = colorchooser.askcolor(title="Choose Button Color", color=ROBLOX_COLORS["button"])[1]
    
    if background_color and text_color and button_color:
        ROBLOX_COLORS["background"] = background_color
        ROBLOX_COLORS["text"] = text_color
        ROBLOX_COLORS["button"] = button_color
        log("Roblox colors updated successfully!")

def locate_roblox_files():
    roblox_path = filedialog.askdirectory(title="Select Roblox Installation Directory")
    if roblox_path:
        log(f"Roblox files located at: {roblox_path}")

def copy_roblox_files():
    try:
        local_appdata = os.getenv("LOCALAPPDATA")
        local_low_appdata = os.getenv("LOCALAPPDATA").replace("Local", "LocalLow")
        
        roblox_paths = [
            os.path.join(local_appdata, "Roblox"),
            os.path.join(local_low_appdata, "Roblox")
        ]
        
        for path in roblox_paths:
            if os.path.exists(path):
                dest_path = os.path.join(CUSTOM_ROBLOX_DIR, os.path.basename(path))
                shutil.copytree(path, dest_path, dirs_exist_ok=True)
                log(f"Copied files from {path} to {dest_path}")
            else:
                log(f"Directory not found: {path}")
        
        log("Roblox files copied successfully!")
    except Exception as e:
        log(f"Failed to copy Roblox files: {e}")

root = tk.Tk()
root.title("CevStrap - Custom Roblox Launcher")
root.geometry("800x600")
root.configure(bg=BG_COLOR)

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background=BG_COLOR)
style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR)
style.configure("TButton", background=BUTTON_COLOR, foreground=FG_COLOR)
style.configure("TEntry", fieldbackground=ENTRY_COLOR, foreground=TEXT_COLOR)
style.configure("TListbox", background=ENTRY_COLOR, foreground=TEXT_COLOR)
style.configure("TScrolledText", background=ENTRY_COLOR, foreground=TEXT_COLOR)

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

install_tab = ttk.Frame(notebook)
notebook.add(install_tab, text="Install Roblox")

install_label = tk.Label(install_tab, text="Install Roblox to the CustomRoblox directory:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
install_label.pack(pady=10)

install_button = tk.Button(install_tab, text="Install Roblox", command=install_roblox, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
install_button.pack(pady=10)

fastflags_tab = ttk.Frame(notebook)
notebook.add(fastflags_tab, text="FastFlags")

fastflags_label = tk.Label(fastflags_tab, text="Manage FastFlags:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
fastflags_label.pack(pady=10)

fastflags_listbox = tk.Listbox(fastflags_tab, width=70, height=10, font=("Arial", 12), bg=ENTRY_COLOR, fg=TEXT_COLOR)
fastflags_listbox.pack(pady=10)

add_button = tk.Button(fastflags_tab, text="Add FastFlag", command=add_fastflag, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
add_button.pack(side=tk.LEFT, padx=5)

remove_button = tk.Button(fastflags_tab, text="Remove FastFlag", command=remove_fastflag, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
remove_button.pack(side=tk.LEFT, padx=5)

multi_instance_tab = ttk.Frame(notebook)
notebook.add(multi_instance_tab, text="Multi-Instance")

multi_instance_label = tk.Label(multi_instance_tab, text="Launch multiple instances of Roblox:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
multi_instance_label.pack(pady=10)

multi_instance_button = tk.Button(multi_instance_tab, text="Launch Multi-Instance", command=launch_multi_instance, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
multi_instance_button.pack(pady=10)

customization_tab = ttk.Frame(notebook)
notebook.add(customization_tab, text="Customization")

customization_label = tk.Label(customization_tab, text="Customize Roblox Colors:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
customization_label.pack(pady=10)

customize_button = tk.Button(customization_tab, text="Customize Colors", command=customize_roblox_colors, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
customize_button.pack(pady=10)

studio_tab = ttk.Frame(notebook)
notebook.add(studio_tab, text="Roblox Studio")

studio_label = tk.Label(studio_tab, text="Launch Roblox Studio:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
studio_label.pack(pady=10)

studio_button = tk.Button(studio_tab, text="Launch Studio", command=launch_roblox_studio, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
studio_button.pack(pady=10)

locate_tab = ttk.Frame(notebook)
notebook.add(locate_tab, text="Locate Files")

locate_label = tk.Label(locate_tab, text="Locate Roblox Installation Files:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
locate_label.pack(pady=10)

locate_button = tk.Button(locate_tab, text="Locate Files", command=locate_roblox_files, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
locate_button.pack(pady=10)

copy_tab = ttk.Frame(notebook)
notebook.add(copy_tab, text="Copy Files")

copy_label = tk.Label(copy_tab, text="Copy Roblox Files from AppData:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR)
copy_label.pack(pady=10)

copy_button = tk.Button(copy_tab, text="Copy Files", command=copy_roblox_files, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
copy_button.pack(pady=10)

launch_button = tk.Button(root, text="Launch Roblox", command=launch_roblox, font=("Arial", 14), bg="green", fg=FG_COLOR)
launch_button.pack(pady=10)

log_area = ScrolledText(root, width=80, height=10, font=("Arial", 12), bg=ENTRY_COLOR, fg=TEXT_COLOR)
log_area.pack(pady=10, fill=tk.BOTH, expand=True)
log_area.config(state=tk.DISABLED)

config_frame = tk.Frame(root, bg=BG_COLOR)
config_frame.pack(pady=10)

save_button = tk.Button(config_frame, text="Save Config", command=save_config, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
save_button.pack(side=tk.LEFT, padx=5)

load_button = tk.Button(config_frame, text="Load Config", command=load_config, font=("Arial", 12), bg=BUTTON_COLOR, fg=FG_COLOR)
load_button.pack(side=tk.LEFT, padx=5)

load_config()

root.mainloop()