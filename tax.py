import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

data = pd.read_csv('incomeoutcome.csv')
print(data.columns)
columns_to_check = ['수출 중량', '수출 금액', '수입 중량', '수입 금액', '무역수지']
data_cleaned = data[~(data[columns_to_check] == 0).all(axis=1)]
print(data_cleaned)
data_cleaned.to_csv('data.csv', index=False,encoding='utf-8-sig')