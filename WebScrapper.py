# -*- coding: utf-8 -*-
"""BlackcofferAssignment.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I80xqsZjnRYrstDBuam7kQnR_0NUt5IH
"""

# Install required libraries
!pip install beautifulsoup4 requests chardet pandas openpyxl

# Import necessary libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import re
import chardet

from google.colab import files
uploaded = files.upload()

input_data = pd.read_excel('Input.xlsx')

input_data.head()

# Scraping Function
def scrape_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1').get_text() if soup.find('h1') else ''
        paragraphs = soup.find_all('p')
        article_text = '\n'.join([para.get_text() for para in paragraphs])
        full_text = f"{title}\n{article_text}"
        return full_text
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

# directory for saving articles
os.makedirs('articles', exist_ok=True)

valid_urls = []

# Scrape articles
for index, row in input_data.iterrows():
    url = row['URL']
    url_id = row['URL_ID']
    article_text = scrape_article(url)
    if article_text:
        with open(f'articles/{url_id}.txt', 'w', encoding='utf-8') as file:
            file.write(article_text)
        valid_urls.append({'URL_ID': url_id, 'URL': url})
        print(f"Article {url_id} saved.")
    else:
        print(f"Failed to scrape {url}")

# Convert valid URLs to a DataFrame
valid_urls_df = pd.DataFrame(valid_urls)

valid_urls_df.head()

uploaded = files.upload()

positive_words = []
negative_words = []

with open('positive-words.txt', 'r', encoding='ascii') as file:
    positive_words = file.read().splitlines()

with open('negative-words.txt', 'r', encoding='ISO-8859-1') as file:
    negative_words = file.read().splitlines()

print(f"Positive words count: {len(positive_words)}")
print(f"Negative words count: {len(negative_words)}")

uploaded = files.upload()

stop_words_files = [
    'StopWords_Auditor.txt',
    'StopWords_Currencies.txt',
    'StopWords_DatesandNumbers.txt',
    'StopWords_Generic.txt',
    'StopWords_GenericLong.txt',
    'StopWords_Geographic.txt',
    'StopWords_Names.txt'
]

stop_words_encodings = {
    'StopWords_Auditor.txt': 'ascii',
    'StopWords_Currencies.txt': 'ISO-8859-1',
    'StopWords_DatesandNumbers.txt': 'ascii',
    'StopWords_Generic.txt': 'ascii',
    'StopWords_GenericLong.txt': 'ascii',
    'StopWords_Geographic.txt': 'ascii',
    'StopWords_Names.txt': 'ascii'
}

def read_stop_words(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as file:
        stop_words = file.read().splitlines()
    return stop_words

# Dictionary to store stopwords
stop_words_dict = {}

# Reading stop words from each file using detected encodings
for file_path in stop_words_files:
    encoding = stop_words_encodings[file_path]
    stop_words = read_stop_words(file_path, encoding)
    stop_words_dict[file_path] = stop_words

for file_path, stop_words in stop_words_dict.items():
    print(f"{file_path} stop words count: {len(stop_words)}")

def get_words_excluding_stopwords(text, stop_words_dict):
    words = text.split()
    all_stop_words = []
    for stop_words in stop_words_dict.values():
        all_stop_words.extend(stop_words)
    return [word for word in words if word.lower() not in all_stop_words]

def get_positive_score(text):
    words = get_words_excluding_stopwords(text, stop_words_dict)
    positive_score = sum(1 for word in words if word.lower() in positive_words)
    return positive_score

def get_negative_score(text):
    words = get_words_excluding_stopwords(text, stop_words_dict)
    negative_score = sum(1 for word in words if word.lower() in negative_words)
    return negative_score

def get_polarity_score(positive_score, negative_score):
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    return polarity_score

def get_subjectivity_score(positive_score, negative_score, total_words):
    subjectivity_score = (positive_score + negative_score) / (total_words + 0.000001)
    return subjectivity_score

def get_avg_sentence_length(text):
    sentences = text.split('.')
    words = text.split()
    avg_sentence_length = len(words) / len(sentences)
    return avg_sentence_length

def count_syllables(word):
    word = word.lower()
    vowels = "aeiouy"
    num_vowels = 0
    prev_char_was_vowel = False
    for char in word:
        if char in vowels:
            if not prev_char_was_vowel:
                num_vowels += 1
            prev_char_was_vowel = True
        else:
            prev_char_was_vowel = False
    if word.endswith("e"):
        num_vowels -= 1
    if num_vowels == 0:
        num_vowels = 1
    return num_vowels

def get_complex_word_count(text):
    words = text.split()
    complex_words = [word for word in words if count_syllables(word) >= 3]
    return len(complex_words)

def get_percentage_complex_words(complex_word_count, total_words):
    percentage_complex_words = (complex_word_count / total_words) * 100
    return percentage_complex_words

def get_fog_index(avg_sentence_length, percentage_complex_words):
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    return fog_index

def get_avg_words_per_sentence(avg_sentence_length):
    return avg_sentence_length

def get_word_count(text):
    words = text.split()
    return len(words)

def get_syllables_per_word(text):
    words = text.split()
    total_syllables = sum(count_syllables(word) for word in words)
    syllables_per_word = total_syllables / len(words)
    return syllables_per_word

def get_personal_pronouns(text):
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)
    return len(pronouns)

def get_avg_word_length(text):
    words = text.split()
    total_length = sum(len(word) for word in words)
    avg_word_length = total_length / len(words)
    return avg_word_length

results = []

for index, row in valid_urls_df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    with open(f'articles/{url_id}.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    positive_score = get_positive_score(text)
    negative_score = get_negative_score(text)
    polarity_score = get_polarity_score(positive_score, negative_score)
    total_words = get_word_count(text)
    subjectivity_score = get_subjectivity_score(positive_score, negative_score, total_words)
    avg_sentence_length = get_avg_sentence_length(text)
    complex_word_count = get_complex_word_count(text)
    percentage_complex_words = get_percentage_complex_words(complex_word_count, total_words)
    fog_index = get_fog_index(avg_sentence_length, percentage_complex_words)
    avg_words_per_sentence = get_avg_words_per_sentence(avg_sentence_length)
    syllables_per_word = get_syllables_per_word(text)
    personal_pronouns = get_personal_pronouns(text)
    avg_word_length = get_avg_word_length(text)

    results.append({
        'URL_ID': url_id,
        'URL': url,
        'POSITIVE_SCORE': positive_score,
        'NEGATIVE_SCORE': negative_score,
        'POLARITY_SCORE': polarity_score,
        'SUBJECTIVITY_SCORE': subjectivity_score,
        'AVG_SENTENCE_LENGTH': avg_sentence_length,
        'PERCENTAGE_COMPLEX_WORDS': percentage_complex_words,
        'FOG_INDEX': fog_index,
        'AVG_WORDS_PER_SENTENCE': avg_words_per_sentence,
        'COMPLEX_WORD_COUNT': complex_word_count,
        'WORD_COUNT': total_words,
        'SYLLABLES_PER_WORD': syllables_per_word,
        'PERSONAL_PRONOUNS': personal_pronouns,
        'AVG_WORD_LENGTH': avg_word_length
    })

# Converting the results to a DataFrame
results_df = pd.DataFrame(results)

# Reordering the columns
results_df = results_df[['URL_ID', 'URL', 'POSITIVE_SCORE', 'NEGATIVE_SCORE', 'POLARITY_SCORE', 'SUBJECTIVITY_SCORE', 'AVG_SENTENCE_LENGTH', 'PERCENTAGE_COMPLEX_WORDS', 'FOG_INDEX', 'AVG_WORDS_PER_SENTENCE', 'COMPLEX_WORD_COUNT', 'WORD_COUNT', 'SYLLABLES_PER_WORD', 'PERSONAL_PRONOUNS', 'AVG_WORD_LENGTH']]

# Save results to CSV
results_df.to_csv('text_analysis_results.csv', index=False)

print("Text analysis completed and results saved to 'text_analysis_results.csv'.")