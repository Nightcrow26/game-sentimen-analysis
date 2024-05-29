import streamlit as st
import pandas as pd
import joblib
from preprocessing import normalisasi, stopword, stemming

# Load model and vectorizer
model = joblib.load('nb.pkl')
vectorizer = joblib.load('tfidf.pkl')

# Set up the main title and sidebar options
st.set_page_config(page_title="Sentiment Analysis GAME", layout="wide")
st.title('Sentiment Analysis GAME with NAIVE BAYES + TFIDF')

st.sidebar.header('Input Options')
option = st.sidebar.radio('Choose Input Option:', ['Text', 'File'])


# Function to map predictions to labels
def map_prediction(pred):
    return 'Positif' if pred == 1 else 'Negatif'


# Process text input
if option == 'Text':
    st.header('Text Input')
    user_input = st.text_area('Enter Text:', '')
    if st.button('Analyze'):
        # Preprocess text
        Normalisasi = normalisasi(user_input)
        Stopword = stopword(Normalisasi)
        Tokenisasi = Stopword.split()
        Stemming = stemming(Tokenisasi)

        # Display preprocessing steps
        st.subheader('Preprocessing Steps:')
        steps = pd.DataFrame({
            'Step': ['Normalisasi', 'Stopword Removal', 'Tokenization', 'Stemming'],
            'Result': [Normalisasi, Stopword, Tokenisasi, Stemming]
        })
        st.dataframe(steps)

        # Transform and predict sentiment
        new_data_tfidf = vectorizer.transform([Stemming])
        new_data_tfidf = new_data_tfidf.toarray()
        prediction = model.predict(new_data_tfidf)
        sentiment = map_prediction(prediction[0])

        # Display sentiment with appropriate color
        if sentiment == 'Negatif':
            st.markdown(f'<span style="color:red;">Sentiment: {sentiment}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="color:green;">Sentiment: {sentiment}</span>', unsafe_allow_html=True)

# Process file input
elif option == 'File':
    st.header('File Input')
    uploaded_file = st.file_uploader('Upload Excel/CSV File:', type=['csv', 'xlsx'])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)

        # Preprocess text column
        df['text'] = df['text'].astype(str)
        df['Normalisasi'] = df['text'].apply(normalisasi)
        df['Stopword Removal'] = df['Normalisasi'].apply(stopword)
        df['Tokenisasi'] = df['Stopword Removal'].apply(lambda x: x.split())
        df['Stemming'] = df['Tokenisasi'].apply(stemming)

        # Transform and predict sentiment
        new_data_tfidf = vectorizer.transform(df['Stemming'])
        new_data_tfidf = new_data_tfidf.toarray()
        predictions = model.predict(new_data_tfidf)
        df['Sentiment'] = predictions
        df['Sentiment'] = df['Sentiment'].apply(map_prediction)

        # Display sentiment distribution
        st.subheader('Sentiment Distribution:')
        sentiment_counts = df['Sentiment'].value_counts()

        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(sentiment_counts)
        with col2:
            st.write(sentiment_counts)

        # Display preprocessing steps in a more detailed manner
        st.subheader('Preprocessing Steps:')
        st.dataframe(df[['text', 'Normalisasi', 'Stopword Removal', 'Tokenisasi', 'Stemming', 'Sentiment']])
