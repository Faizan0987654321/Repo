import datetime
import win32com.client
from bs4 import BeautifulSoup

def calculate_runtime(start_time, end_time):
    start_datetime = datetime.datetime.strptime(start_time, '%m/%d/%Y %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_time, '%m/%d/%Y %H:%M:%S')
    runtime = end_datetime - start_datetime
    return runtime

def create_html_table(data):
    grouped_data = {}
    
    # Group tasks and calculate average runtime
    for task in data:
        task_name = task['name']
        if task_name.startswith('Task Faizan'):
            task_name = 'All Faizan'

        if task_name not in grouped_data:
            grouped_data[task_name] = {
                'total_runtime': calculate_runtime(task['start_time'], task['end_time']),
                'count': 1
            }
        else:
            grouped_data[task_name]['total_runtime'] += calculate_runtime(task['start_time'], task['end_time'])
            grouped_data[task_name]['count'] += 1

    # Calculate average runtime and create HTML table
    table_html = """
    <table style="border-collapse: collapse; width: 100%; text-align: left; border: 2px solid #3498db;">
        <tr style="background-color: #3498db; color: #ffffff;">
            <th style="padding: 10px;">Task</th>
            <th style="padding: 10px;">Average Runtime</th>
        </tr>
    """
    for task_name, task_data in grouped_data.items():
        average_runtime = task_data['total_runtime'] / task_data['count']
        table_html += f"""
        <tr>
            <td style="border: 1px solid #3498db; padding: 8px;">{task_name}</td>
            <td style="border: 1px solid #3498db; padding: 8px;">{str(average_runtime)}</td>
        </tr>
        """
    table_html += "</table>"
    return table_html

def send_email(subject, body):
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.HTMLBody = body
    mail.Display()

def parse_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        rows = soup.find_all('tr')[1:]  # Exclude header row
        task_data = []
        for row in rows:
            columns = row.find_all('td')
            task_data.append({
                'name': columns[0].text.strip(),
                'start_time': columns[1].text.strip(),
                'end_time': columns[2].text.strip(),
            })
        return task_data

# Replace "success.html" with the actual path to your HTML file
html_file_path = "success.html"
tasks_data = parse_html_file(html_file_path)

subject = "Task Runtimes Report"
body = create_html_table(tasks_data)

send_email(subject, body)
