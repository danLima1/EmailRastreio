from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

def enviar_email(to_email, full_name, tracking_code, numero_pedido, previsao_entrega):
    from_email = "promosaude@lojavitalife.com.br"  # E-mail profissional da Hostinger
    from_name = "Rastreamento"
    password = "Googleads123@"  # Senha do e-mail do remetente
    smtp_server = "smtp.hostinger.com"
    smtp_port = 587  # Porta TLS (pode usar 465 se for SSL)

    nome_cliente = full_name
    data_envio = datetime.now().strftime('%d/%m/%Y')  # Data atual
    subject = "Código de Rastreio do seu Pedido"

    # Template HTML fornecido
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Código de Rastreio do seu Pedido</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .logo {
                text-align: center;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            .logo svg {
                width: 32px;
                height: 32px;
                color: #6a3de8;
            }
            .logo-text {
                color: #6a3de8;
                font-size: 28px;
                font-weight: bold;
                text-decoration: none;
            }
            .container {
                background-color: #f8f7ff;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                border: 1px solid #e6e3ff;
            }
            .tracking-code {
                background-color: #f0ebff;
                padding: 15px;
                border-radius: 5px;
                font-size: 18px;
                text-align: center;
                margin: 20px 0;
                border: 1px solid #d9d1ff;
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                background-color: #6a3de8;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
                transition: background-color 0.3s;
            }
            .button:hover {
                background-color: #5632c0;
            }
            h2 {
                color: #6a3de8;
            }
            .footer {
                margin-top: 30px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <path d="M3.29 7 12 12l8.71-5"></path>
                <line x1="12" y1="22" x2="12" y2="12"></line>
            </svg>
            <span class="logo-text">FastTracker</span>
        </div>
        <div class="container">
            <h2>Olá {nome_cliente},</h2>
            
            <p>Ótimas notícias! Seu pedido #{numero_pedido} já está a caminho.</p>
            
            <p>Aqui está seu código de rastreio:</p>
            
            <div class="tracking-code">
                <strong>{codigo_rastreio}</strong>
            </div>
            
            <p>Você pode acompanhar seu pedido clicando no botão abaixo:</p>
            
            <center>
                <a href="http://localhost:5000/{codigo_rastreio}" class="button">Rastrear Pedido</a>
            </center>
            
            <p>Informações do pedido:</p>
            <ul>
                <li>Número do pedido: #{numero_pedido}</li>
                <li>Data do envio: {data_envio}</li>
                <li>Previsão de entrega: {previsao_entrega}</li>
            </ul>
            
            <p>Se precisar de ajuda, não hesite em nos contatar.</p>
            
            <p>Atenciosamente,<br>
            FastTracker</p>
        </div>
        
        <div class="footer">
            <p>Este é um email automático, por favor não responda.</p>
            <p>© 2024 FastTracker - Todos os direitos reservados</p>
        </div>
    </body>
    </html>
    """

    # Substituição dos placeholders
    html_content = html_template.format(
        nome_cliente=nome_cliente,
        numero_pedido=numero_pedido,
        codigo_rastreio=tracking_code,
        data_envio=data_envio,
        previsao_entrega=previsao_entrega
    )

    # Construindo o e-mail
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adicionando o corpo HTML ao e-mail
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Conectando ao servidor SMTP e enviando o e-mail
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Inicia conexão TLS
        server.login(from_email, password)  # Autenticação
        server.sendmail(from_email, to_email, msg.as_string())  # Enviando e-mail
        server.quit()
        print(f"E-mail enviado para {to_email}.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

@app.route('/webhook2', methods=['POST'])
def webhook2():
    data = request.json
    customer = data.get('customer', {})
    email = customer.get('email')
    full_name = customer.get('name')

    if not email or not full_name:
        return jsonify({'status': 'error', 'message': 'Dados incompletos'}), 400

    try:
        # Enviando os dados para a API que gera o código de rastreamento
        response = requests.post('https://nightmarish-fishsticks-ggqgpqjx9x4f9jj7-5000.app.github.dev/webhook', json=data)
        print(f"Response status: {response.status_code}, Response content: {response.content.decode()}")

        if response.status_code != 200:
            return jsonify({'status': 'error', 'message': 'Falha ao gerar código de rastreamento'}), 500

        tracking_data = response.json()
        tracking_code = tracking_data.get('code')
        previsao_entrega = tracking_data.get('previsao_entrega', 'Não disponível')

        # Se você tiver um número de pedido no data, use-o:
        numero_pedido = data.get('order_number', 'Indisponível')

        if tracking_code:
            # Enviando o e-mail para o cliente com o código de rastreamento
            enviar_email(email, full_name, tracking_code, numero_pedido, previsao_entrega)
            return jsonify({'status': 'success', 'message': 'E-mail enviado com sucesso'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Código de rastreamento não encontrado'}), 500

    except Exception as e:
        print(f"Erro no processamento do webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True)
