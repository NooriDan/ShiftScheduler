import subprocess
import os
import platform

def run_servers():
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    webapp_dir = os.path.join(base_dir, "ta-scheduling-webapp")
    frontend_dir = os.path.join(base_dir, "ta-scheduling-frontend")

    system = platform.system()
    processes = []  # Make sure to define the processes list

    if system == "Darwin":  # macOS
        print("Detected macOS")
        # Set Terminal window titles for macOS
        processes.append(subprocess.Popen(
            ["osascript", "-e", f'tell application "Terminal" to do script "cd {webapp_dir} && echo WebApp Server && run-app"']
        ))
        processes.append(subprocess.Popen(
            ["osascript", "-e", f'tell application "Terminal" to do script "cd {frontend_dir} && echo Frontend Server && npm run dev"']
        ))

    elif system == "Linux":  # Linux
        print("Detected Linux")
        # Set Terminal window titles for Linux (gnome-terminal)
        processes.append(subprocess.Popen(
            ["bash", "-c", f"cd {webapp_dir} && echo 'WebApp Server' && run-app; exec bash"]
        ))
        processes.append(subprocess.Popen(
            ["bash", "-c", f"cd {frontend_dir} && echo 'Frontend Server' && npm run dev; exec bash"]
        ))

    elif system == "Windows":  # Windows
        print("Detected Windows")
        # Set Command Prompt titles for Windows
        processes.append(subprocess.Popen(
            ["cmd.exe", "/k", f"cd /d {webapp_dir} && echo WebApp Server && run-app"], shell=True
        ))
        processes.append(subprocess.Popen(
            ["cmd.exe", "/k", f"cd /d {frontend_dir} && echo Frontend Server && npm run dev"], shell=True
        ))

    else:
        print(f"Unsupported OS: {system}")

    print(f"Process IDs: {[process.pid for process in processes]}")

if __name__ == "__main__":
    # Run the servers
    run_servers()
