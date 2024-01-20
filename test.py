import datetime
import win32com.client
from bs4 import BeautifulSoup

def calculate_runtime(start_time, end_time):
    start_datetime = datetime.datetime.strptime(start_time, '%m/%d/%Y %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_time, '%m/%d/%Y %H:%M:%S')
    return end_datetime - start_datetime

def create_html_table(grouped_data):
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

def filter_tasks_by_group(task_data, group_keywords):
    return [task for task in task_data if any(keyword in task['name'] for keyword in group_keywords)]

def group_and_average_tasks(tasks_data, group_name, group_keywords):
    filtered_tasks = filter_tasks_by_group(tasks_data, group_keywords)
    grouped_data = {}
    for task in filtered_tasks:
        task_name = group_name
        if task_name not in grouped_data:
            grouped_data[task_name] = {
                'total_runtime': calculate_runtime(task['start_time'], task['end_time']),
                'count': 1
            }
        else:
            grouped_data[task_name]['total_runtime'] += calculate_runtime(task['start_time'], task['end_time'])
            grouped_data[task_name]['count'] += 1
    return grouped_data

# Replace "success.html" with the actual path to your HTML file
html_file_path = "success.html"
tasks_data = parse_html_file(html_file_path)

# Grouped Data
faizan_grouped_data = group_and_average_tasks(tasks_data, 'All Faizan', ['Task Faizan'])
group2_grouped_data = group_and_average_tasks(tasks_data, 'Group 2', ['Different Task'])
practical_grouped_data = group_and_average_tasks(tasks_data, 'Practical Tasks', ['cust', 'const'])

# Single Tasks
single_tasks = [task for task in tasks_data if task['name'] in ['Hardcoded 1', 'Hardcoded 2']]
single_grouped_data = {}
for task in single_tasks:
    task_name = task['name']
    single_grouped_data[task_name] = {
        'total_runtime': calculate_runtime(task['start_time'], task['end_time']),
        'count': 1
    }

# Combine all grouped data
all_grouped_data = {**faizan_grouped_data, **group2_grouped_data, **practical_grouped_data, **single_grouped_data}

# Create a single HTML table for all groups
all_table_html = create_html_table(all_grouped_data)

# Send a single email with all tables
subject_all = "Task Runtimes Report - All Groups"
send_email(subject_all, all_table_html)
