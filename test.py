import tkinter as tk
from tkinter import messagebox 
from joblib import load
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load
from tkinter import ttk

# Load data from Excel file
file_path = 'incidents.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Preprocessing: Remove punctuation and convert to lowercase
def preprocess_text(text):
    if isinstance(text, str):
        text = text.lower().replace('\n', ' ')
    return text

# Apply preprocessing to description and summary columns
df['description'] = df['description'].apply(preprocess_text)

# Combine 'description' and 'class' columns for TF-IDF vectorization
combined_text = df['description'] + ' ' + df['class']

# TF-IDF vectorization on description
tfidf_vectorizer = TfidfVectorizer()
combined_tfidf_matrix = tfidf_vectorizer.fit_transform(combined_text)

# Build K-NN model using combined TF-IDF matrix
knn_model = NearestNeighbors(n_neighbors=6, metric='cosine') # for first run
knn_model.fit(combined_tfidf_matrix)
dump(knn_model, 'trained_model.joblib')  # Save the trained model to a file

# Function to find similar incidents and display in tabs
def find_similar():
    user_description = entry.get("1.0", tk.END)
    if user_description.strip():
        user_description = preprocess_text(user_description)
        user_vector = tfidf_vectorizer.transform([user_description])
        distances, indices = knn_model.kneighbors(user_vector)

        # Initialize variables for tab names and contents
        tab_names = ["Similar 1", "Similar 2", "Similar 3", "Similar 4", "Similar 5"]
        tab_contents = []

        # Iterate over top 5 similar incidents
        for i in range(1, 6):
            similar_incident_index = indices[0][i]
            similar_incident_number = df.iloc[similar_incident_index]['incident_number']
            similar_summary = df.iloc[similar_incident_index]['summary']
            similar_class = df.iloc[similar_incident_index]['class']
            tab_content = f"INC : {similar_incident_number}\nSummary: {similar_summary}\nClass: {similar_class}"
            tab_contents.append(tab_content)

        # Create a new Tkinter window for displaying similar incidents
        global message_box
        message_box = tk.Tk()
        message_box.title("Similar Incidents")

        # Create tabs within the window
        notebook = ttk.Notebook(message_box, width=600, height=600)
        for name, content in zip(tab_names, tab_contents):
            frame = tk.Frame(notebook)
            notebook.add(frame, text=name)
            label = tk.Label(frame, text=content, padx=20, pady=20, font=("Arial", 12), wraplength=500, anchor="w")  # Adjust wrap length and anchor
            label.pack()

        notebook.pack()
        message_box.mainloop()
    else:
        messagebox.showwarning("Warning", "Please enter an incident description.")

# GUI setup with styles and colors
root = tk.Tk()
root.title("Incident Similarity Finder")
root.geometry("1000x500")  # Set window size
root.configure(bg='#f0f0f0')  # Set background color of the window

# Label for entering incident description
label = tk.Label(root, text="Enter Incident Description:", bg='#f0f0f0', fg='blue', font=('Arial', 12, 'bold'))
label.pack(padx=10, pady=10)

# Text input area for incident description
entry = tk.Text(root, width=50, height=10, wrap=tk.WORD, font=('Arial', 10))  # Larger text input area
entry.pack()

# Button for finding similar incidents
button = tk.Button(root, text="Find Similar Incidents", command=find_similar, bg='green', fg='white', font=('Arial', 10, 'bold'))
button.pack(padx=10, pady=10)

root.mainloop()

# commands to make changes in repo
# git add .
# git commit -m "message"
# git push origin master