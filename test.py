import subprocess

def open_safari():
    try:
        # Using subprocess to run Safari
        subprocess.run(['open', '-a', 'Safari'])
    except FileNotFoundError:
        print("Error: Safari is not installed on this system.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
open_safari()