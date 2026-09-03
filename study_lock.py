import json
import random
import time
import os
import sys
import threading
from datetime import datetime
import ctypes
import win32gui
import win32con
from PIL import Image, ImageTk
import base64
import io
import urllib.request
from urllib.parse import urlparse

# pip install -r requirements.txt
# python study_lock.py

class StudyLock:
    def __init__(self, questions_file="questions.json", lock_time=1800):
        self.questions_file = questions_file
        self.lock_time = lock_time
        self.questions = self.load_questions()
        self.current_question = None
        self.lock_window = None
        self.is_locked = False
        self.timer_thread = None
        self.image_cache = {}
        self.answer_correct = False
        self.waiting_for_answer = False
        
    def load_questions(self):
        """Load questions from JSON file with support for images and alerts"""
        default_questions = [
            {
                "question": "2+2",
                "answer": "4",
                "image": "https://placeholdit.com/600x400",
                "alert": "The answer is 4"
            }
        ]
        
        try:
            if os.path.exists(self.questions_file):
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    for q in questions:
                        if "image" not in q:
                            q["image"] = None
                        if "alert" not in q:
                            q["alert"] = None
                    return questions
            else:
                with open(self.questions_file, 'w', encoding='utf-8') as f:
                    json.dump(default_questions, f, ensure_ascii=False, indent=2)
                return default_questions
        except Exception as e:
            print(f"Error loading questions: {e}")
            return default_questions
    
    def save_questions(self):
        """Save questions to file"""
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)
    
    def get_random_question(self):
        """Get random question"""
        return random.choice(self.questions)
    
    def download_image_from_url(self, url):
        """Download image from URL and return base64 encoded string"""
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                raise ValueError("Invalid URL format")
            
            with urllib.request.urlopen(url, timeout=10) as response:
                img_data = response.read()
                content_type = response.headers.get('Content-Type', '')
                ext = content_type.split('/')[-1] if '/' in content_type else 'jpeg'
                
                base64_str = base64.b64encode(img_data).decode('utf-8')
                return f"data:image/{ext};base64,{base64_str}"
        except Exception as e:
            print(f"Error downloading image from URL: {e}")
            return None
    
    def load_image_data(self, image_input):
        """Load image from file path, URL, or base64 string"""
        if not image_input:
            return None
        
        try:
            # Check if it's a URL
            if image_input.startswith(('http://', 'https://')):
                return self.download_image_from_url(image_input)
            
            # Check if it's a file path
            if os.path.exists(image_input):
                with open(image_input, 'rb') as img_file:
                    img_data = img_file.read()
                    ext = os.path.splitext(image_input)[1].lower()
                    mime_type = {
                        '.jpg': 'jpeg',
                        '.jpeg': 'jpeg', 
                        '.png': 'png',
                        '.gif': 'gif',
                        '.bmp': 'bmp',
                        '.webp': 'webp'
                    }.get(ext, 'jpeg')
                    
                    base64_str = base64.b64encode(img_data).decode('utf-8')
                    return f"data:image/{mime_type};base64,{base64_str}"
            
            # Check if it's already a base64 string
            if image_input.startswith('data:image') or len(image_input) > 100:
                return image_input
            
            return None
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def load_image(self, image_data, max_width=800, max_height=600):
        """Load image with scaling"""
        if not image_data:
            return None
            
        try:
            img = None
            
            # If it's a file path
            if isinstance(image_data, str):
                if os.path.exists(image_data):
                    img = Image.open(image_data)
                # If it's a base64 string
                elif image_data.startswith('data:image') or len(image_data) > 100:
                    try:
                        if ',' in image_data:
                            image_data = image_data.split(',')[1]
                        img_data = base64.b64decode(image_data)
                        img = Image.open(io.BytesIO(img_data))
                    except:
                        return None
            
            if img:
                # Scale image while maintaining aspect ratio
                img_width, img_height = img.size
                
                # Calculate new dimensions
                if img_width > max_width or img_height > max_height:
                    ratio = min(max_width / img_width, max_height / img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    
                    # Use high-quality scaling
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                return ImageTk.PhotoImage(img)
            
            return None
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def create_lock_window(self, test_mode=False):
        """Create lock window with support for images and alerts"""
        import tkinter as tk
        from tkinter import messagebox
        
        # Destroy existing window if it exists
        if self.lock_window:
            try:
                self.lock_window.destroy()
            except:
                pass
        
        self.lock_window = tk.Tk()
        
        if test_mode:
            self.lock_window.title("TEST LOCK")
        else:
            self.lock_window.title("ANSWER REQUIRED!")
            
        self.lock_window.attributes('-fullscreen', True)
        self.lock_window.attributes('-topmost', True)
        
        # Block window closing via ALT+F4 or close button
        self.lock_window.protocol("WM_DELETE_WINDOW", self.prevent_close)
        
        self.current_question = self.get_random_question()
        
        # Get screen dimensions for proper scaling
        screen_width = self.lock_window.winfo_screenwidth()
        screen_height = self.lock_window.winfo_screenheight()
        
        # Calculate maximum image dimensions
        max_image_width = int(screen_width * 0.8)
        max_image_height = int(screen_height * 0.5)
        
        frame = tk.Frame(self.lock_window, bg='#2c3e50')
        frame.pack(expand=True, fill='both')
        
        if test_mode:
            title_text = "TEST LOCK\n\nAnswer the question to verify the system"
            title_color = '#27ae60'
        else:
            title_text = "Time to study!\n\nAnswer the question to continue working"
            title_color = '#f39c12'
        
        label = tk.Label(frame, 
                        text=title_text,
                        font=('Arial', 24),
                        bg='#2c3e50',
                        fg=title_color,
                        pady=20)
        label.pack()
        
        # Display question
        question_label = tk.Label(frame,
                                 text=f"Question: {self.current_question['question']}",
                                 font=('Arial', 20),
                                 bg='#2c3e50',
                                 fg='#3498db',
                                 wraplength=int(screen_width * 0.9),
                                 pady=10)
        question_label.pack()
        
        # Display image if present
        self.photo = None  # Keep reference to image
        if self.current_question.get('image'):
            self.photo = self.load_image(self.current_question['image'], 
                                       max_width=max_image_width, 
                                       max_height=max_image_height)
            if self.photo:
                image_label = tk.Label(frame, image=self.photo, bg='#2c3e50')
                image_label.pack(pady=20)
        
        answer_var = tk.StringVar()
        entry = tk.Entry(frame,
                        textvariable=answer_var,
                        font=('Arial', 18),
                        width=min(80, int(screen_width / 20)),
                        justify='center')
        entry.pack(pady=20)
        entry.focus()
        
        def check_answer():
            user_answer = answer_var.get().strip()
            correct_answer = str(self.current_question['answer']).strip()
            
            if not user_answer:
                messagebox.showwarning("Warning", "Please enter an answer!")
                return
            
            if user_answer == correct_answer:
                # Show alert if present
                if self.current_question.get('alert') and self.current_question['alert']:
                    messagebox.showinfo("Information", self.current_question['alert'])
                
                self.answer_correct = True
                self.waiting_for_answer = False
                self.lock_window.destroy()
                self.lock_window = None
            else:
                # Show alert if present
                if self.current_question.get('alert') and self.current_question['alert']:
                    messagebox.showinfo("Information", self.current_question['alert'])
                
                messagebox.showerror("Incorrect!", "Try again!")
                entry.delete(0, tk.END)
                entry.focus()
        
        submit_btn = tk.Button(frame,
                              text="Check answer" if not test_mode else "Check (test)",
                              command=check_answer,
                              font=('Arial', 16),
                              bg='#3498db',
                              fg='white',
                              padx=30,
                              pady=10)
        submit_btn.pack(pady=20)
        
        # Bind Enter key to check answer
        entry.bind('<Return>', lambda event: check_answer())
        
        # Make window modal
        self.lock_window.grab_set()
        self.lock_window.focus_force()
    
    def prevent_close(self):
        """Prevent window closing"""
        pass
    
    def show_lock_window(self, test_mode=False):
        """Show lock window and wait for answer"""
        self.answer_correct = False
        self.waiting_for_answer = True
        self.create_lock_window(test_mode)
        
        if self.lock_window:
            # Run Tkinter main loop for this window
            self.lock_window.mainloop()
    
    def add_question_with_image(self, question, answer, image_path=None, image_url=None, alert=None):
        """Add question with image from file or URL"""
        image_data = None
        
        if image_path:
            image_data = self.load_image_data(image_path)
        elif image_url:
            image_data = self.load_image_data(image_url)
        
        self.questions.append({
            "question": question,
            "answer": answer,
            "image": image_data,
            "alert": alert
        })
        self.save_questions()
        print(f"Added new question: {question}")
        if image_path or image_url:
            print(f"Image added: {image_path or image_url}")
        if alert:
            print(f"Alert added: {alert}")
    
    def add_question(self, question, answer, alert=None):
        """Add question without image"""
        self.questions.append({
            "question": question,
            "answer": answer,
            "image": None,
            "alert": alert
        })
        self.save_questions()
        print(f"Added new question: {question}")
    
    def remove_question(self, index):
        """Remove question by index"""
        if 0 <= index < len(self.questions):
            removed = self.questions.pop(index)
            self.save_questions()
            print(f"Removed question: {removed['question']}")
            return True
        return False
    
    def list_questions(self):
        """List all questions"""
        print("\n" + "="*60)
        print("QUESTION LIST:")
        print("="*60)
        for i, q in enumerate(self.questions, 1):
            has_image = "YES" if q.get('image') else "no"
            has_alert = "YES" if q.get('alert') and q['alert'] else "no"
            question_text = q['question'][:60] + "..." if len(q['question']) > 60 else q['question']
            print(f"{i:2d}. {question_text:<65} -> {q['answer']:>10} [image: {has_image}] [alert: {has_alert}]")
        print("="*60)
    
    def block_system(self, test_mode=False):
        """Block the system"""
        self.is_locked = True
        
        if test_mode:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] TEST lock!")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] System locked!")
        
        if not test_mode:
            self.minimize_all_windows()
        
        # Show window and wait for answer
        self.show_lock_window(test_mode)
        
        # After window closes
        self.is_locked = False
        
        if self.answer_correct:
            if not test_mode:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Correct answer! Lock removed.")
                self.start_timer()
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Test passed successfully!")
            return True
        else:
            return False
    
    def minimize_all_windows(self):
        """Minimize all windows"""
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        
        win32gui.EnumWindows(callback, None)
    
    def timer_loop(self):
        """Main timer loop"""
        while True:
            time.sleep(self.lock_time)
            if not self.is_locked:
                self.block_system()
    
    def start_timer(self):
        """Start the timer"""
        if self.timer_thread and self.timer_thread.is_alive():
            return
        
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer started. Next lock in {self.lock_time//60} minutes")

def auto_start_with_test(minutes=30):
    """Automatic startup with test lock and custom interval"""
    print("="*60)
    print("STUDY LOCK - AUTOMATIC STARTUP")
    print("="*60)
    print(f"Lock interval: {minutes} minutes")
    print("="*60)
    
    lock = StudyLock(lock_time=minutes * 60)
    
    # Start timer
    lock.start_timer()
    
    # Start test lock after 3 seconds
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting test lock in 3 seconds...")
    time.sleep(3)
    lock.block_system(test_mode=True)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Test passed! Continue working.")
    print(f"Next lock in {minutes} minutes.")
    print("Program is running in background.")
    print("-"*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nLock stopped!")
        sys.exit(0)

def main():
    print("="*60)
    print("STUDY LOCK v3.0 - WITH IMAGE AND ALERT SUPPORT")
    print("Computer will lock at regular intervals")
    print("Answer questions to continue working")
    print("="*60)
    
    lock = StudyLock(lock_time=1800)
    
    while True:
        try:
            print("\nMENU:")
            print("1. Start lock (with test lock)")
            print("2. Start lock")
            print("3. Add question without image")
            print("4. Add question with image (file or URL)")
            print("5. Remove question")
            print("6. Show all questions")
            print("7. Change interval (in minutes)")
            print("8. Exit")
            
            choice = input("\nChoose action (1-8): ").strip()
            
            if choice == "1":
                try:
                    minutes = input("Enter interval in minutes (default 30): ").strip()
                    if minutes:
                        minutes = int(minutes)
                    else:
                        minutes = 30
                    print(f"\nStarting lock with test... Interval: {minutes} minutes")
                    print(f"First test lock, then regular every {minutes} minutes.")
                    print("-"*60)
                    
                    lock.lock_time = minutes * 60
                    lock.start_timer()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting test lock...")
                    time.sleep(2)
                    lock.block_system(test_mode=True)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Test passed! Continue working.")
                    print(f"Next lock in {minutes} minutes.")
                    print("Program is running in background. Do not close this window.")
                    print("Press Ctrl+C to stop")
                    print("-"*60)
                    
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\nLock stopped! Returning to menu...")
                        continue
                except ValueError:
                    print("Invalid input! Please enter a number.")
                    
            elif choice == "2":
                try:
                    minutes = input("Enter interval in minutes for auto-lock (default 30): ").strip()
                    if minutes:
                        minutes = int(minutes)
                    else:
                        minutes = 30
                    
                    # Set the lock time
                    lock.lock_time = minutes * 60
                    
                    # Show lock immediately
                    print(f"\nShowing lock immediately!")
                    print(f"After answering correctly, next lock will be in {minutes} minutes.")
                    print("-"*60)
                    
                    # Block the system immediately
                    lock.block_system(test_mode=False)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Lock removed! Timer started.")
                    print(f"Next lock in {minutes} minutes.")
                    print("Program is running in background. Do not close this window.")
                    print("Press Ctrl+C to stop")
                    print("-"*60)
                    
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\nLock stopped! Returning to menu...")
                        continue
                except ValueError:
                    print("Invalid input! Please enter a number.")
                    
            elif choice == "3":
                question = input("Enter question: ").strip()
                answer = input("Enter answer: ").strip()
                alert = input("Enter alert message (Enter to skip): ").strip()
                if not alert:
                    alert = None
                if question and answer:
                    lock.add_question(question, answer, alert)
                else:
                    print("Question and answer cannot be empty!")
                    
            elif choice == "4":
                question = input("Enter question: ").strip()
                answer = input("Enter answer: ").strip()
                alert = input("Enter alert message (Enter to skip): ").strip()
                if not alert:
                    alert = None
                
                print("Add image from:")
                print("1. File path")
                print("2. URL")
                image_choice = input("Choose option (1-2, Enter to skip): ").strip()
                
                if image_choice == "1":
                    image_path = input("Enter image file path: ").strip()
                    if question and answer:
                        if image_path:
                            lock.add_question_with_image(question, answer, image_path=image_path, alert=alert)
                        else:
                            lock.add_question(question, answer, alert)
                elif image_choice == "2":
                    image_url = input("Enter image URL: ").strip()
                    if question and answer:
                        if image_url:
                            lock.add_question_with_image(question, answer, image_url=image_url, alert=alert)
                        else:
                            lock.add_question(question, answer, alert)
                else:
                    if question and answer:
                        lock.add_question(question, answer, alert)
                    else:
                        print("Question and answer cannot be empty!")
                    
            elif choice == "5":
                lock.list_questions()
                try:
                    index = int(input("Enter question number to remove: ")) - 1
                    if lock.remove_question(index):
                        print("Question removed!")
                    else:
                        print("Invalid question number!")
                except:
                    print("Invalid input!")
                    
            elif choice == "6":
                lock.list_questions()
                
            elif choice == "7":
                try:
                    minutes = int(input("Enter interval in minutes: "))
                    lock.lock_time = minutes * 60
                    print(f"Interval changed to {minutes} minutes")
                except:
                    print("Invalid input!")
                    
            elif choice == "8":
                print("Exiting...")
                sys.exit(0)
                
            else:
                print("Invalid choice!")
                
        except KeyboardInterrupt:
            print("\n\nCtrl+C pressed! Returning to menu...")
            continue

if __name__ == "__main__":
    # Check installed libraries
    try:
        import win32gui
        import win32con
        from PIL import Image, ImageTk
    except ImportError:
        print("Please install required libraries:")
        print("pip install pywin32 Pillow")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--autostart" or arg == "/autostart":
            # Check if minutes parameter is provided
            if len(sys.argv) > 2:
                try:
                    minutes = int(sys.argv[2])
                    auto_start_with_test(minutes)
                except ValueError:
                    print("Invalid minutes value. Using default 30 minutes.")
                    auto_start_with_test(30)
            else:
                auto_start_with_test(30)
        elif arg == "--help" or arg == "-h":
            print("Study Lock - A productivity tool that locks your PC with questions")
            print("\nUsage:")
            print("  python study_lock.py                      - Run in interactive mode")
            print("  python study_lock.py --autostart [minutes] - Run automatically with test lock")
            print("  python study_lock.py --help               - Show this help message")
            print("\nExamples:")
            print("  python study_lock.py --autostart          - Start with default 30 minutes")
            print("  python study_lock.py --autostart 15       - Start with 15 minutes interval")
            print("  python study_lock.py --autostart 45       - Start with 45 minutes interval")
            print("\nFeatures:")
            print("  - Lock PC at configurable intervals")
            print("  - Answer questions to unlock")
            print("  - Support for images (file or URL)")
            print("  - Support for alert messages")
            sys.exit(0)
        else:
            print("Unknown argument. Use --help for usage information.")
            sys.exit(1)
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\nProgram stopped by user. Goodbye!")
            sys.exit(0)