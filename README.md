# 📄 Boleto PDF Processor API

## Descrição

A Boleto PDF Processor API é uma aplicação Flask projetada para processar e extrair informações de boletos em formato PDF. A API recebe arquivos PDF, identifica o tipo de documento e extrai campos essenciais como código de instalação, código do usuário, vencimento, valor total, código de barras, entre outros. Essas informações são então armazenadas em um banco de dados SQLite para facilitar consultas futuras.

## Funcionalidades Principais
- Extração de Texto de PDFs: A API utiliza a biblioteca pymupdf para ler e extrair o texto de PDFs.
- Identificação de Boletos: A API diferencia tipos de boletos com base em textos específicos.
- Extração de Dados: Extrai campos como código de instalação, código do usuário, data de vencimento, valor total e código de barras através de expressões regulares.
- Armazenamento em Banco de Dados: As informações extraídas são salvas em um banco de dados SQLite utilizando SQLAlchemy.
- Tratamento de Erros: Implementação robusta de tratamento de erros para garantir que a API seja resiliente a entradas inesperadas ou malformadas.

## Endpoints

- **POST /processar_boletos_pdfs**: Endpoint principal que recebe um ou mais arquivos PDF e processa cada um individualmente. O retorno é um JSON com o status de processamento de cada arquivo.

## Como Usar

**Clone o Repositório**

```bash
    git clone https://github.com/seuusuario/seurepositorio.git
    cd seurepositorio
```
**Instale as dependências**

```bash
    pip install requirements.txt
```
**Execute a aplicação**

```bash
    python main.py
```
**Faça Upload de PDFs**

Utilize ferramentas como curl, Postman, ou outra de sua escolha para enviar uma requisição POST para http://localhost:5000/processar_boletos_pdfs com os arquivos PDF.

Exemplo usando curl:

```bash
    curl -F "file=@caminho/do/arquivo.pdf" http://localhost:5000/processar_boletos_pdfs
```
**Verifique o resultado**

A resposta incluirá detalhes sobre o processamento de cada arquivo PDF, como informações extraídas ou erros encontrados.

**Exemplo de JSON Retornado**

```bash
    [
  {
    "detalhes": "Boleto processado e salvo com sucesso.",
    "boleto": {
      "boleto_tipo": "internet",
      "codigo_instalacao": "123456789012",
      "codigo_usuario": "9876543210",
      "vencimento": "15/08/2024",
      "valor_total": "150.00",
      "cod_barras": "12345678901234567890123456789012345678901234",
      "cnpj_concessionaria": "00.00.000/0000-00"
    }
  }
]
```

## Dependências
- **Flask**: Framework web utilizado para construir a API.
- **pymupdf**: Biblioteca para leitura e extração de textos de arquivos PDF.
- **SQLAlchemy**: ORM utilizado para interagir com o banco de dados SQLite.
- **datetime e re**: Bibliotecas padrão do Python para manipulação de datas e expressões regulares.

## Estrutura de Projeto
- **main.py**: Código principal da aplicação Flask.
- **requirements.txt**: Lista de dependências Python necessárias.
- **boleto.db**: Arquivo de banco de dados SQLite que armazena as informações extraídas dos boletos.

## Considerações finais

A Boleto PDF Processor API é uma solução prática para automatizar o processamento de boletos, economizando tempo e reduzindo a margem de erro em comparação com a extração manual de dados. Com uma arquitetura modular e robusta, essa API pode ser facilmente expandida para lidar com diferentes tipos de documentos e outras fontes de dados.

💡 **Dica**: Certifique-se de testar a API com diferentes tipos de boletos e adaptar as expressões regulares conforme necessário para garantir que todos os dados sejam extraídos corretamente.
