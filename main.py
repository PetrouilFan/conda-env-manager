import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import threading

class CondaEnvironmentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Conda Environment Manager")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and pack widgets
        self.create_widgets()
        self.refresh_environments()

    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.main_frame, text="Conda Environment Manager", 
                              font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Environment listbox
        self.env_listbox = tk.Listbox(self.main_frame, width=50, height=15)
        self.env_listbox.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", 
                                command=self.env_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.env_listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons
        refresh_btn = ttk.Button(self.main_frame, text="Refresh List", 
                               command=self.refresh_environments)
        refresh_btn.grid(row=2, column=0, pady=10, padx=5)

        delete_btn = ttk.Button(self.main_frame, text="Delete Selected", 
                              command=self.delete_environment)
        delete_btn.grid(row=2, column=1, pady=10, padx=5)

        clean_btn = ttk.Button(self.main_frame, text="Clean Conda", 
                             command=self.clean_conda)
        clean_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def get_conda_environments(self):
        try:
            result = subprocess.run(['conda', 'env', 'list', '--json'], 
                                 capture_output=True, text=True)
            environments = json.loads(result.stdout)
            return environments['envs']
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get conda environments: {str(e)}")
            return []

    def refresh_environments(self):
        self.env_listbox.delete(0, tk.END)
        environments = self.get_conda_environments()
        for env in environments:
            self.env_listbox.insert(tk.END, env)

    def delete_environment(self):
        selection = self.env_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an environment to delete")
            return

        env_path = self.env_listbox.get(selection[0])
        env_name = env_path.split('\\')[-1]  # Get the environment name from path

        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete the environment '{env_name}'?"):
            # Start deletion in background
            def delete_thread():
                try:
                    subprocess.run(['conda', 'env', 'remove', '--name', env_name, '-y'], 
                                 check=True, capture_output=True, text=True)
                    # Use after to safely update GUI from thread
                    self.root.after(0, lambda: messagebox.showinfo("Success", 
                                  f"Environment '{env_name}' deleted successfully"))
                    self.root.after(0, self.refresh_environments)
                except subprocess.CalledProcessError as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", 
                                  f"Failed to delete environment: {e.stderr}"))
            
            thread = threading.Thread(target=delete_thread)
            thread.daemon = True  # Thread will exit when main program exits
            thread.start()
            # Immediately refresh to show operation is in progress
            self.refresh_environments()

    def clean_conda(self):
        try:
            result = subprocess.run(['conda', 'clean', '-a', '-y'], 
                                 capture_output=True, text=True, check=True)
            print(result.stdout)
            messagebox.showinfo("Success", "Conda cleaned successfully")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to clean conda: {e.stderr}")

def main():
    root = tk.Tk()
    app = CondaEnvironmentManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()