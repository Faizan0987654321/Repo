# from transformers import pipeline

# # Load the sentiment analysis model
# sentiment_analysis = pipeline("sentiment-analysis")

# # Define a list of texts to analyze
# texts = [
#     "I love this product!",
#     "This movie was terrible.",
#     "The food at this restaurant is amazing.",
#     "I'm feeling neutral about this.",
# ]

# # Analyze the sentiment of each text
# for text in texts:
#     result = sentiment_analysis(text)
#     print(f"Text: {text}")
#     print(f"Sentiment: {result[0]['label']}")
#     print(f"Confidence: {result[0]['score']}")
#     print()

#  using TFDistilBertForSequenceClassification for pre trained model
from transformers import TFDistilBertForSequenceClassification, DistilBertTokenizer
import tensorflow as tf

# Load the pre-trained model and tokenizer
model = TFDistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

# Define a text to classify
text = "I am not really sure about this."

# Tokenize the text
inputs = tokenizer(text, return_tensors="tf")

# Perform the classification
outputs = model(inputs)
predictions = tf.nn.softmax(outputs.logits, axis=1).numpy()[0]

# Print the results
print(f"Text: {text}")
print(f"Positive: {predictions[1]}")
print(f"Negative: {predictions[0]}")

# for subsequent use
# Save the model
# model.save_pretrained("model")

# # Save the tokenizer
# tokenizer.save_pretrained("model")

# # Load the model and tokenizer
# model = TFDistilBertForSequenceClassification.from_pretrained("model")
# tokenizer = DistilBertTokenizer.from_pretrained("model")

# # Define a text to classify
# text = "I am neutral"

# # Tokenize the text
# inputs = tokenizer(text, return_tensors="tf")

# # Perform the classification
# outputs = model(inputs)
# predictions = tf.nn.softmax(outputs.logits, axis=1).numpy()[0]

# # Print the results
# print(f"Text: {text}")
# print(f"Positive: {predictions[1]}")
# print(f"Negative: {predictions[0]}")


