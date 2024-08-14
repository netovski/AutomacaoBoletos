from flask import Flask, request, jsonify
import pymupdf
import re
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import traceback

# Função de conectar ao banco de dados
DATABASE_URL = "sqlite:///./boleto.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Classe base para as tabelas do banco
class Boleto(Base):
    __tablename__ = "boletos"
    id = Column(Integer, primary_key=True, index=True)
    boleto_tipo = Column(String)
    codigo_instalacao = Column(String, index=True)
    codigo_usuario = Column(String)
    vencimento = Column(String)
    valor_total = Column(String)
    cod_barras = Column(String)
    cnpj_concessionaria = Column(String)

Base.metadata.create_all(bind=engine)

# Inicio da API
app = Flask(__name__)

# Função para extrair os textos do PDF
def extract_text_from_pdf(pdf_content):
    pdf_document = pymupdf.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Dicionario de meses
months = {
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05',
    'jun': '06', 'jul': '07', 'ago': '08', 'set': '09', 'out': '10',
    'nov': '11', 'dez': '12'
}

# Função para formatar as datas
def extract_and_format_date(text):
    date_pattern = r'(\d{2}/\d{2}/\d{4})|(\d{2})\s(\w{3})\s(\d{2})'
    matches = re.findall(date_pattern, text)
    
    formatted_dates = []
    for match in matches:
        if match[0]:  # Formato dd/mm/yyyy
            formatted_dates.append(match[0])
        else:  # Formato dd mmm yy
            day, month_text, year = match[1], match[2], match[3]
            month = months.get(month_text.lower())
            if month:
                formatted_date = f'{day}/{month}/20{year}'
                formatted_dates.append(formatted_date)
    
    return formatted_dates

# Função para extrair campos específicos do boleto
def extract_fields(text):
    formatted_dates = extract_and_format_date(text)

    # Templates Regex para buscar informações chave
    codigo_instalacao = re.search(r'\b(\d{12})\b', text) # Coloque o formato do jeito que você quer localizar o codigo
    codigo_usuario = re.search(r'\b(\d{8,11})\b', text)  
    vencimento = max(formatted_dates, default=None, key=lambda date: datetime.strptime(date, '%d/%m/%Y')) if formatted_dates else None
    valor_total = re.search(r'R\$\s*([\d.,]+)', text) 
    cod_barras = re.search(r'((\d{11})\-(\d{1})\s*(\d{11})\-(\d{1})\s*(\d{11})\-(\d{1})\s*(\d{11})\-(\d{1}))', text) 

    return {
        # Return que busca as informações no primeiro match que encontra com as especificações do Regex
        "boleto_tipo": "internet",
        "codigo_instalacao": codigo_instalacao.group(1).replace("/", "") if codigo_instalacao else None,
        "codigo_usuario": codigo_usuario.group(1).replace(" ", "") if codigo_usuario else None,
        "vencimento": vencimento,
        "valor_total": valor_total.group(1) if valor_total else None,
        "cod_barras": cod_barras.group(1).replace("-", "").replace(" ", "") if cod_barras else None,
        "cnpj_concessionaria": "00.00.000/0000-00" # Dados ficticios
    }

# Função que identifica o boleto e caracteriza ele pelo tipo
def identifica_documento(text):
    if "Alguma frase para identificar o boleto" in text:
        return "boleto_internet", extract_fields
    return None, None

# Inicia o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função já alinhada ao POST da aplicação, faz todas as ligações necessárias com as respostas HTTP
def processar_boletos(file):
    if not file.filename.endswith('.pdf'):
        return {"detalhes": "Arquivo não é um PDF."}, 400

    try:
        # Lê o arquivo PDF em binário
        pdf_content = file.read()
        if not pdf_content:
            return {"detalhes": "O arquivo está vazio ou não pôde ser lido."}, 400

        text = extract_text_from_pdf(pdf_content)
        if not text:
            return {"detalhes": "O texto não pôde ser extraído."}, 400

        documento_tipo, processamento_funcao = identifica_documento(text)
        if not processamento_funcao:
            return {"detalhes": "Tipo de boleto não reconhecido."}, 400

        dados = processamento_funcao(text)

        campos_faltando = [campo for campo, valor in dados.items() if not valor]

        if campos_faltando:
            return {
                "detalhes":"Dados incompletos, não foi possível salvar. ",
                "campos_faltando": campos_faltando
            }, 400
        db = next(get_db())
        novo_boleto = Boleto(**dados)
        db.add(novo_boleto)
        db.commit()
        db.refresh(novo_boleto)

        return {"detalhes": "Boleto processado e salvo com sucesso.", "boleto": dados}, 201

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro ao processar o arquivo: {e}")
        print(f"Detalhes do erro: {error_details}")
        return {"detalhes": f"Erro ao processar o arquivo: {str(e)}"}, 500

@app.route('/processar_boletos_pdfs', methods=['POST'])
def upload_pdfs():
    files = request.files.getlist('file')

    print(f"Arquivos recebidos: {[file.filename for file in files]}")

    if not files or len(files) == 0:
        return jsonify({"erro": "Não há arquivos para a requisição"}), 400
    
    results = []

    for file in files:
        # Processar cada arquivo PDF
        result, status_code = processar_boletos(file)
        results.append(result)

    return jsonify(results), 207


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


