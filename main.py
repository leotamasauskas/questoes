from flask import Flask, render_template, request
import PyPDF2
from nltk.tokenize import sent_tokenize, word_tokenize
import string
from nltk.corpus import stopwords
import random
import io
import nltk
nltk.download('stopwords')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

def ler_pdf(arquivo_pdf):
    leitor_pdf = PyPDF2.PdfReader(arquivo_pdf)
    texto = ''
    for pagina in leitor_pdf.pages:
        texto += pagina.extract_text()
    return texto

def preprocessar_texto(texto):
    sentencas = sent_tokenize(texto)
    tokens = [word_tokenize(sentenca.lower()) for sentenca in sentencas]
    tokens = [[palavra for palavra in sentenca if palavra not in string.punctuation and palavra not in stopwords.words('portuguese')] for sentenca in tokens]
    return tokens

def criar_questoes(tokens, num_questoes=5):
    questoes = []
    for _ in range(num_questoes):
        sentenca = random.choice(tokens)
        palavra = random.choice(sentenca)
        questao = ' '.join(sentenca).replace(palavra, '_______')

        # Verificar se a lista sentenca tem pelo menos 4 elementos
        if len(sentenca) >= 4:
            palavras_chave = random.sample(sentenca, k=3)
        else:
            palavras_chave = random.sample(sentenca, k=len(sentenca) - 1)

        alternativas = [palavra] + palavras_chave
        random.shuffle(alternativas)
        questoes.append((questao, alternativas))
    return questoes





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_questoes', methods=['POST'])
def gerar_questoes():
    if 'pdf' not in request.files:
        return render_template('index.html', error='Nenhum arquivo PDF foi enviado.')
    
    arquivo_pdf = request.files['pdf']
    if arquivo_pdf.filename == '':
        return render_template('index.html', error='Nenhum arquivo selecionado.')
    
    texto = ler_pdf(arquivo_pdf)
    if not texto:
        return render_template('index.html', error='Falha ao ler o arquivo PDF.')
    
    tokens = preprocessar_texto(texto)
    if not tokens:
        return render_template('index.html', error='Não foi possível pré-processar o texto do PDF.')
    
    questoes = criar_questoes(tokens)
    if not questoes:
        return render_template('index.html', error='Não foi possível gerar as questões.')
    
    return render_template('questoes.html', questoes=questoes)

if __name__ == '__main__':
    app.run(debug=True)

