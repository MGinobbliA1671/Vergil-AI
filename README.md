# INSTRUTIONS TO RUN VERGIL AI

#NOTE: the API key of the groq AI and firebase will expire, so please replace it so it will work

#1. Clone the Repository
```bash
git clone https://github.com/MGinobbliA1671/Vergil-AI.git
cd Vergil-AI


#2. Create a Virtual Environment

python -m venv venv
venv\Scripts\activate         #windows
source venv/bin/activate      # On macOS/Linux

#3. Install Dependencies
pip install -r requirements.txt

#4. Run the Streamlit App
streamlit run app.py

#5. Open the localhost in browser
http://localhost:8501
