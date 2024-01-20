import os
import win32com.client as win32
from bs4 import BeautifulSoup
import re
from datetime import datetime
import shutil
from tkinter import *
from tkinter import WORD, messagebox
import tkinter as tk
import subprocess
import sys
import logging

try:

    # start time
    start_time = datetime.now().strftime("%H:%M:%S")

    # Path to the shared drive (replace with your shared drive path)
    shared_drive_path = r"C:\User Items\Projects\SP 3"

    # Create the logs folder in the shared drive if it doesn't exist
    logs_folder = os.path.join(shared_drive_path, 'Logs')
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Configure logging to save logs in the shared drive folder
    log_format = '%(asctime)s - %(message)s'
    log_file_name = os.path.join(logs_folder, f"CheckPoint_Log_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.txt")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format=log_format)

    logging.info(os.getlogin() + "launched CheckPoint")

    # preidm logic
    def get_preidm_logs():
        global preidm_logs
        preidm_logs = []
        # Specify the directory path for the PREIDM folder
        preidm_directories = [
            ('Dev', r'C:\User Items\Projects\SP 2\PREIDM'),
            ('Prod', r'C:\User Items\Projects\SP 2\PREIDM 1'),
            ('Prod', r'C:\User Items\Projects\SP 2\PREIDM 2'),
        ]

        for label, preidm_directory in preidm_directories:
            drive, folder = os.path.splitdrive(preidm_directory)
            
            with os.scandir(preidm_directory) as entries:
                text_files = [entry.name for entry in entries if entry.is_file() and entry.name.endswith('.txt')]

            if not text_files:
                write_to_output(f"{drive} - {label} No text files found in the PREIDM folder.")
                return "No text files found in the PREIDM folder."

            latest_file = max(text_files, key=lambda x: os.path.getmtime(os.path.join(preidm_directory, x)))

            with open(os.path.join(preidm_directory, latest_file), 'r') as file:
                content = file.read()

            threshold_matches = re.findall(r'Delete threshold: (\d+)', content)
            preidm_finished = "preidm finished" in content.lower()
            no_dept_found = "id found with no dept" in content.lower()

            if not threshold_matches or not preidm_finished:
                preidm_logs.append(
                    f"{drive} - {label} PreIDM Failed.")
                write_to_output(f"{drive} - {label} PreIDM Failed.")
            else:
                delete_threshold = int(threshold_matches[-1])
                preidm_logs.append(
                    f"{drive} - {label} Delete threshold: {delete_threshold}")
                write_to_output(f"{drive} - {label} Delete threshold: {delete_threshold}")
            if no_dept_found:   
                preidm_logs.append(
                    f"{drive} - ID found with no dept")
                write_to_output(f"{drive} - ID found with no dept")

        return preidm_logs

    # mirpt logic
    def get_mirpt_logs():
        global mirpt_logs
        mirpt_logs = []
        mirpt_directories = [
            r'C:\User Items\Projects\SP 2\MIRPT Logs'
        ]

        for mirpt_directory in mirpt_directories:
            with os.scandir(mirpt_directory) as entries:
                text_files = [entry.name for entry in entries if entry.is_file() and entry.name.endswith('.txt')]

            if not text_files:
                mirpt_logs.append(
                    f"{os.path.basename(mirpt_directory)} - No text files found.")
                write_to_output(f"{os.path.basename(mirpt_directory)} - No text files found.")
                continue

            latest_file = max(text_files, key=lambda x: os.path.getmtime(os.path.join(mirpt_directory, x)))

            with open(os.path.join(mirpt_directory, latest_file), 'r') as file:
                last_line = file.readlines()[-1].strip()

            if "no adhoc requests pending" in last_line.lower():
                mirpt_logs.append(
                    f"{os.path.basename(mirpt_directory)} - SUCCESS")
                write_to_output(f"{os.path.basename(mirpt_directory)} - SUCCESS")
            else:
                mirpt_logs.append(
                    f"{os.path.basename(mirpt_directory)} - FAILED")
                write_to_output(f"{os.path.basename(mirpt_directory)} - FAILED")

        return mirpt_logs

    def report_bug():
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)  # 0 represents an email item
            mail.To = 'IAMOperations@example.com'  
            mail.Subject = 'CheckOut App Bug Report - ' + str(today)
            mail.HTMLBody = "Please describe your issue here."
            mail.Display()
        except Exception as e:
            messagebox.showerror("Error", f"Error while reporting bug: {str(e)}")
            logging.error(f"Error while reporting bug: {str(e)}")

    def write_to_output(text):
        output_text.configure(state="normal", fg="black", font=("Arial", 12))
        output_text.insert("end", f"{text}\n")
        logging.info(text)
        output_text.configure(state="disabled")

    def table_creator():
        # Regular expression pattern to match tasks starting with 'Task Faizan', 'const', or 'cust'
        pattern_faizan = re.compile(r'^Task Faizan.*')
        pattern_const_cust = re.compile(r'^(const|cust).*')

        # hardcoded tasks
        hardcoded_tasks = ['Hardcoded 1', 'Hardcoded 2', 'Hardcoded 3', 'Hardcoded 11']

        try:
            # Define source directories
            source_directories = {
                'IA': r'C:\Users\faiza\Desktop\IA',
                'MO': r'C:\Users\faiza\Desktop\MO',
                'Prod': r'C:\Users\faiza\Desktop\Prod'
            }
        except Exception as e:
            logging.error(f"Error while defining source directories: {str(e)}")
            return
        
        try:
            # Destination directories in the current location
            destination_directories = {
                'IA': './IA/',
                'MO': './MO/',
                'Prod': './Prod/'
            }
        except Exception as e:
            logging.error(f"Error while defining destination directories: {str(e)}")
            return

        # Function to copy latest files from source directory to destination directory
        def copy_latest_files(source_dir, destination_dir):
            try:
                # Clear the destination directory
                shutil.rmtree(destination_dir, ignore_errors=True)
                logging.info(f"Deleted files from {destination_dir}")
        
                # Create the destination directory
                os.makedirs(destination_dir, exist_ok=True)
                files = [f for f in os.listdir(source_dir) if f.endswith('.html')]
                files.sort(key=lambda x: os.path.getmtime(os.path.join(source_dir, x)), reverse=True)
                latest_files = files[:4]

                for file_name in latest_files:
                    source_path = os.path.join(source_dir, file_name)
                    destination_path = os.path.join(destination_dir, file_name)
                    shutil.copyfile(source_path, destination_path)
            except Exception as e:
                logging.error(f"Error while copying files from {source_dir} to {destination_dir}: {str(e)}")

        # Copy HTML files from source directories to destination directories
        for env, source_dir in source_directories.items():
            try:
                write_to_output(f"Trying to bring files...")
                os.makedirs(destination_directories[env], exist_ok=True)
                destination_dir = destination_directories[env]
                copy_latest_files(source_dir, destination_dir)
                write_to_output(f"Files copied from {source_dir} to {destination_dir}")
            except Exception as e:
                logging.error(f"Error while creating destination directory {destination_dir}: {str(e)}")

        # Create the confirmation message with the list of files
        message = "The following files will be used to generate the Task Status Report:\n\n"

        for env, destination_dir in destination_directories.items():
            files = [f for f in os.listdir(destination_dir) if f.endswith('.html')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(destination_dir, x)), reverse=True)
            latest_files = files[:4]
            message += f"{env}:\n"
            for file_name in latest_files:
                message += f"{file_name}\n"
            message += "\n"

        # Ask for confirmation using a message box
        confirmed = messagebox.askyesno("Confirmation", message)

        # If the user confirms, proceed with generating the email
        if confirmed:
            pass
        else:
            write_to_output("Email generation cancelled.")
            return
        
        def get_latest_files(destination_dir):
            try:
                files = [os.path.join(destination_dir, f) for f in os.listdir(destination_dir) if f.endswith('.html')]
                files.sort(key=os.path.getmtime, reverse=True)
                return files[:4]
            except Exception as e:
                print(f"Error fetching files from {destination_dir}: {str(e)}")
                return []
            
        # Function to get tasks and their statuses from an HTML file
        def get_tasks_and_status_from_html(file_path):
            tasks = []
            try:
                with open(file_path, 'r') as html_file:
                    html_content = html_file.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    # Find all td elements containing task names
                    td_elements = soup.find_all('td')
                    task_data = []

                    for td in td_elements:
                        task_name = td.get_text().strip()
                        # Check if the task matches the pattern and add it to the list
                        if pattern_faizan.match(task_name) or pattern_const_cust.match(task_name) or task_name in hardcoded_tasks:
                            status = file_path.split('\\')[-1].split(' - ')[1].split('(')[0].strip()
                            # Replace 'Error' status with 'Failed'
                            status = 'Failed' if status == 'Errors' else status
                            tasks.append((task_name, status))
                                               
            except Exception as e:
                logging.error(f"Error while fetching tasks from {file_path}: {str(e)}")
            return tasks

        # Fetch and process files from source directories
        tasks_by_env = {}
        for env, _dir in destination_directories.items():
            destination_dir = destination_directories[env]
            latest_files = get_latest_files(_dir)
            tasks_with_status = []
            for file in latest_files:
                tasks_with_status.extend(get_tasks_and_status_from_html(file))
            tasks_by_env[env] = list(set(tasks_with_status))

        # Create HTML for the email body with a table and summary section
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            logging.info("Drafting email body")
            html_body = f"""
            <html>
            <head></head>
            <body>
                <p style='font-size: 20px'>Tasks and Environment Status for {current_date}:</p>
                <table style="border-collapse: collapse; border: 1px solid #ADD8E6; width: 100%; max-width: 1200px; text-align: center; font-size: 20px;">
                <tr>
                    <th style="background-color: #ADD8E6; padding: 12px;">Task Name</th>
                    <th style="background-color: #ADD8E6; padding: 12px;">IA</th>
                    <th style="background-color: #ADD8E6; padding: 12px;">MO</th>
                    <th style="background-color: #ADD8E6; padding: 12px;">Prod</th>
                </tr>
            """
        except Exception as e:
            logging.error(f"Error while generating email body: {str(e)}")
            return

        # Merge tasks and statuses for each category
        try:
            merged_tasks = {}
            for env, tasks_status_list in tasks_by_env.items():
                for task, status in tasks_status_list:
                    categorized_task = task
                    if pattern_faizan.match(task):
                        categorized_task = 'All Faizan'
                    elif pattern_const_cust.match(task):
                        categorized_task = 'Practical Tasks'
                    
                    if categorized_task not in merged_tasks:
                        merged_tasks[categorized_task] = {k: [] for k in destination_directories.keys()}
                    
                    merged_tasks[categorized_task][env].append(status)
        except Exception as e:
            logging.error(f"Problem in grouping tasks together: {str(e)}")
            return

        # function to determine the status of a category

        def determine_category_status(statuses):
            if len(statuses) == 0:
                return '-'
            elif 'Failed' in statuses:
                return 'Failed'
            else:
                return 'Success'
            
        # function to set color of the status
            
        def set_color(status):
            if status == 'Success':
                return 'green'
            elif status == 'Failed':
                return 'red'
            else:
                return 'black'
            
        # Fill the table with tasks and their statuses for each environment
        try:
            for task, statuses in merged_tasks.items():
                ia_status = determine_category_status(statuses['IA'])
                mo_status = determine_category_status(statuses['MO'])
                prod_status = determine_category_status(statuses['Prod'])
                
                html_body += f"""
                <tr>
                    <td style="border: 1px solid black; padding: 12px;">{task}</td>
                    <td style="border: 1px solid black; padding: 12px; color: {set_color(ia_status)}">{ia_status}</td>
                    <td style="border: 1px solid black; padding: 12px; color: {set_color(mo_status)}">{mo_status}</td>
                    <td style="border: 1px solid black; padding: 12px; color: {set_color(prod_status)}">{prod_status}</td>
                </tr>
                """
        except Exception as e:
            logging.error(f"Error while filling the staus table: {str(e)}")
            return

        # Complete the HTML table
        html_body += """
            </table>
        """

        # Generate the summary table section
        try:
            logging.info("Drafting summary table")
            summary_table = "<p style='font-size: 20px'>Summary Table:</p>"
            summary_table += "<table style='border-collapse: collapse; border: 1px solid black; width: 100%; max-width: 1000px; text-align: left; font-size: 20px;'><tr><th style='background-color: black; color: white; padding: 12px;'>Entity</th><th style='background-color: black; color: white; padding: 12px;'>Details</th></tr>"

            for env, tasks in tasks_by_env.items():
                failed_tasks = [task for task, status in tasks if status == 'Failed']
                if len(failed_tasks) == 0 and len(tasks) != 0:
                    summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>{env}</td><td style='border: 1px solid black; padding: 12px;'>All tasks ran successfully</td></tr>"
                else:
                    summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>{env}</td><td style='border: 1px solid black; padding: 12px;'>{'<br>'.join(failed_tasks)}</td></tr>"
        except Exception as e:
            logging.error(f"Error while generating summary table: {str(e)}")
            return
        
        # add viper/autosys jobs/pa tester rows to the summary table for (success/failed) as details
        try:
            summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>Viper</td><td style='border: 1px solid black; padding: 12px;'>{viper_status}</td></tr>"
            summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>Autosys Job</td><td style='border: 1px solid black; padding: 12px;'>{autosys_job_status}</td></tr>"
            summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>PA Tester</td><td style='border: 1px solid black; padding: 12px;'>{pa_tester_status}</td></tr>"
            summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>PreIDM</td><td style='border: 1px solid black; padding: 12px;'>{'<br>'.join(preidm_logs)}</td></tr>"
            summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>MIRPT</td><td style='border: 1px solid black; padding: 12px;'>{', '.join(mirpt_logs)}</td></tr>"
            summary_table += f"<tr><td style='border: 1px solid black; padding: 12px;'>ADLDS</td><td style='border: 1px solid black; padding: 12px;'></td></tr>"
            summary_table += "</table>"
        except Exception as e:
            logging.error(f"Error while adding viper/autosys jobs/pa tester rows to the summary table: {str(e)}")
            return

        # Combine the HTML body with the summary table section
        html_body += summary_table

        # Complete the HTML body
        html_body += """
        </body>
        </html>
        """

        # Get current date for subject
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Create an Outlook instance
        try:
            logging.info("Generating email")
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            # Set email properties
            mail.Subject = f'IAM Checkout {current_date}'
            mail.HTMLBody = html_body

            # save email body in C:\checkout reports\Reports as html
            reports_folder = os.path.join(shared_drive_path, 'Reports')
            if not os.path.exists(reports_folder):
                os.makedirs(reports_folder)
            with open(os.path.join(reports_folder, f"{datetime.now().strftime('%Y_%m_%d_%H%M%S')}_IAM_Checkout.html"), 'w') as file:
                file.write(html_body)

            # Display the generated email content in Outlook
            mail.Display()
            write_to_output("Email generated successfully.")
        except Exception as e:
            write_to_output(f"Error while generating email: {str(e)}")
            return

    def create_gui():

        try:
            # create global variables for viper/autosys job/pa tester status
            global viper_status
            global autosys_job_status
            global pa_tester_status
            global preidm_logs
            global mirpt_logs
            viper_status = "-"
            autosys_job_status = "-"
            pa_tester_status = "-"
            preidm_logs = []
            mirpt_logs = []

        except Exception as e:
            logging.error(f"Error while creating global variables: {str(e)}")
            return

        try:

            def toggle_viper():
                global viper_status
                if viper_status == "Success":
                    viper_status = "Failed"
                    button_viper.config(bg="orange", relief="sunken")
                else:
                    viper_status = "Success"
                    button_viper.config(bg="green", relief="sunken")
                logging.info(f"Viper status: {viper_status}")

            def toggle_autosys_job():
                global autosys_job_status
                if autosys_job_status == "Success":
                    autosys_job_status = "Failed"
                    button_autosys_job.config(bg="orange", relief="sunken")
                else:
                    autosys_job_status = "Success"
                    button_autosys_job.config(bg="green", relief="sunken")
                logging.info(f"Autosys job status: {autosys_job_status}")

            def toggle_pa_tester():
                global pa_tester_status
                if pa_tester_status == "Success":
                    pa_tester_status = "Failed"
                    button_pa_tester.config(bg="orange", relief="sunken")
                else:
                    pa_tester_status = "Success"
                    button_pa_tester.config(bg="green", relief="sunken")
                logging.info(f"PA tester status: {pa_tester_status}")

        except Exception as e:
            logging.error(f"Error while toggling viper/autosys job/pa tester: {str(e)}")
            return

        # list of urls to open
        urls = [
        ("Autosys job", ["https://www.google.com", "https://drive.google.com", "https://myaccount.google.com"]),
        ("PA tester", ["https://www.yahoo.com"]),
        ("Viper", ["https://mail.google.com"])
        ]

        # function to open all autosys job urls in browser
        def open_urls():
            for url in urls[0][1]:
                os.startfile(url)
        
        try:
            def on_closing():
                # log current user, start and end time, time spent on app, duration of app. separated by |
                end_time = datetime.now().strftime("%H:%M:%S")
                duration = datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")
                date = datetime.now().strftime("%Y-%m-%d")
                user = os.getlogin()
                logging.info(f"CheckPoint app closed.")
                logging.info(f"User session details\n                          _____________________________________________________________________________________________________")
                # user session details  
                logging.info(f"|User: {user} | Date: {date} | Start time: {start_time} | End time: {end_time} | Time spent: {duration}|\n                          -----------------------------------------------------------------------------------------------------")
                # set log file to read only
                set_file_read_only(log_file_name)
                root.destroy()
        except Exception as e:
            logging.error(f"Error while closing the app: {str(e)}")
            return
        
        def set_file_read_only(file_path):
            try:
                os.chmod(file_path, 0o444)  # Sets read-only permission
            except OSError as e:
                messagebox.showwarning("File Status", f"Unable to set {file_path} to read-only.")

        # create root window
        root = tk.Tk()
        root.title("CheckPoint")
        root.configure(bg="#FFFFFF")
        root.geometry("900x600")
        root.iconbitmap(r'C:\User Items\Projects\SP 3\pin.ico')

        def quit_app():
            logging.info(f"CheckPoint app closed.")
            root.destroy()

        def restart_app():
            python = sys.executable
            logging.info(f"CheckPoint app restarted.")
            script = 'blue.py'
            root.destroy()
            subprocess.call([python, script])

        # About information popup
        def show_about_info():
            message_info = """CheckPoint App Version 1.0

    Developed by:
    - Faizan Shaikh (fshaik10)
    - Sam Pulikkottil (spulik10)

    Features:
    - Comprehensive email reports to document Sailpoint tasks.
    - MIRPT Logs Analysis:  Check synchronization status of ADHoc requests.
    - PRE-IDM Logs Verification: Check delete threshold & verify successful PRE-IDM execution.
    - Conduct validations for Viper/PA Tester/Autosys jobs, executing thorough checks on monitors, servers & services. 

    Feedback and Bug Reporting:
    Got thoughts on how to make CheckPoint even better? Shoot us your feedback and bug reports at fshaik10 & spullik. We're all ears!

    Cheers!
        """
            messagebox.showinfo("About", message_info)

        # Custom font
        custom_font = ("Arial", 12, "bold")

        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # Direct menu to show message_info
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Menu", menu=help_menu)
        help_menu.add_command(label="About", command=show_about_info)
        help_menu.add_command(label="Report Bug", command=report_bug)
        help_menu.add_command(label="Restart", command=restart_app)
        help_menu.add_command(label="Exit", command=quit_app)

        # Branding logo
        logo_image = tk.PhotoImage(file=r'C:\User Items\Projects\SP 3\logo3.png')
        branding_label = tk.Label(root, image=logo_image)
        branding_label.pack(pady=10)

        # Button style definition for consistency
        button_style = {
            # travelers insurance company color cyan background
            "bg": "#04979F",
            "fg": "white",
            "width": 15,
            "height": 2,
            "relief": tk.RAISED,
            "font": custom_font,
        }

        # Create a frame for buttons
        button_frame = tk.Frame(root, bg="#FFFFFF", padx=10, pady=10)
        button_frame.pack()

        # Create buttons and pack them inside the button frame
        button_viper = tk.Button(button_frame, text="Viper", command=toggle_viper, **button_style)
        button_viper.pack(side=tk.LEFT, padx=30, pady=10)

        button_autosys_job = tk.Button(button_frame, text="Autosys Job", command=toggle_autosys_job, **button_style)
        button_autosys_job.pack(side=tk.LEFT, padx=30, pady=10)

        button_pa_tester = tk.Button(button_frame, text="PA Tester", command=toggle_pa_tester, **button_style)
        button_pa_tester.pack(side=tk.LEFT, padx=30, pady=10)

        # Create a frame for the second set of buttons
        second_button_frame = tk.Frame(root, bg="#FFFFFF", padx=10, pady=10)
        second_button_frame.pack()

        button_preidm = tk.Button(second_button_frame, text="PREIDM", command=get_preidm_logs, **button_style)
        button_preidm.pack(side=tk.LEFT, padx=30, pady=10)

        button_mirpt = tk.Button(second_button_frame, text="MIRPT", command=get_mirpt_logs, **button_style)
        button_mirpt.pack(side=tk.LEFT, padx=30, pady=10)

        button_table = tk.Button(second_button_frame, text="Create Report", command=table_creator, **button_style)
        button_table.pack(side=tk.LEFT, padx=30, pady=10)
        
        # Create a frame for hyperlinks
        hyperlink_frame = tk.Frame(root, bg="#FFFFFF", padx=10, pady=10)
        hyperlink_frame.pack()

        # Create hyperlink labels and pack them inside the hyperlink frame
        hyperlink_viper = tk.Label(hyperlink_frame, text="Viper", fg="blue", bg="#FFFFFF", cursor="hand2")
        hyperlink_viper.pack(side=tk.LEFT, padx=10, pady=10)
        hyperlink_viper.bind("<Button-1>", lambda e: os.startfile("https://mail.google.com"))

        hyperlink_autosys_job = tk.Label(hyperlink_frame, text="Autosys job", fg="blue", bg="#FFFFFF", cursor="hand2")
        hyperlink_autosys_job.pack(side=tk.LEFT, padx=10, pady=10)
        hyperlink_autosys_job.bind("<Button-1>", lambda e: open_urls())

        hyperlink_pa_tester = tk.Label(hyperlink_frame, text="PA Tester", fg="blue", bg="#FFFFFF", cursor="hand2")
        hyperlink_pa_tester.pack(side=tk.LEFT, padx=10, pady=10)
        hyperlink_pa_tester.bind("<Button-1>", lambda e: os.startfile("https://www.yahoo.com"))

        # Create an output section
        output_frame = tk.Frame(root, bg="#FFFFFF", padx=10, pady=10)
        output_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        global output_text
        output_text = tk.Text(output_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        output_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=output_text.yview)

        root.protocol("WM_DELETE_WINDOW", on_closing)  # Bind closing action
        root.mainloop()

    create_gui()

except Exception as e:
    logging.error(f"Error while running the app: {str(e)}")
    messagebox.showerror("Error", f"Error while running the app: {str(e)}")

# instructions
# install pyinstaller
# download pin icon
# remove background from pin icon
# set file paths with raw string for icon, logo, etc
# command to compile py -> execute in cmd:  python -m PyInstaller --noconsole --icon=pin.ico --onefile blue.py
# send shortcut to desktop
# test the app