import os
import platform
import subprocess
import signal
import atexit
import time

# List to track processes
processes = []

def run_servers():
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    webapp_dir = os.path.join(base_dir, "ta-scheduling-webapp")
    frontend_dir = os.path.join(base_dir, "ta-scheduling-frontend")

    system = platform.system()

    if system == "Darwin":  # macOS
        print("Detected macOS")
        processes.append(subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "cd {webapp_dir} && run-app"']))
        processes.append(subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "cd {frontend_dir} && npm run dev"']))

    elif system == "Linux":  # Linux
        print("Detected Linux")
        processes.append(subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {webapp_dir} && run-app; exec bash"]))
        processes.append(subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {frontend_dir} && npm run dev; exec bash"]))

    elif system == "Windows":  # Windows
        print("Detected Windows")
        processes.append(subprocess.Popen(["cmd.exe", "/k", f"cd /d {webapp_dir} && run-app"], shell=True))
        processes.append(subprocess.Popen(["cmd.exe", "/k", f"cd /d {frontend_dir} && npm run dev"], shell=True))

    else:
        print(f"Unsupported OS: {system}")

def cleanup_processes():
    """Terminate all child processes when the user chooses to stop them."""
    while True:
        user_input = input("Do you want to terminate all processes? (y/n): ").strip().lower()
        if user_input == "y":
            print("Cleaning up processes...")
            for process in processes:
                try:
                    # Terminate the process
                    process.terminate()
                    process.wait(timeout=5)  # Wait for the process to terminate
                except Exception as e:
                    print(f"Error terminating process{process.pid}: {e}")
                finally:
                    try:
                        # Send SIGKILL if the process is still alive (UNIX-like systems)
                        os.kill(process.pid, signal.SIGKILL)
                    except Exception:
                        pass
            break
        elif user_input == "n":
            print("Processes will continue running. Exiting cleanup.")
            break
        else:
            print("Invalid input. Please enter 'y' to terminate processes or 'n' to keep running.")

if __name__ == "__main__":
    # Run the servers
    run_servers()

    # Call cleanup_processes when the script exits
    # cleanup_processes()
