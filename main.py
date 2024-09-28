from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def enviar_email(to_email, full_name, tracking_code):
    from_email = "envio@rastreamento-distribuidora.shop"  # E-mail profissional da Hostinger
    from_name = "Rastreamento"
    password = "695476Pc@"  # Senha do e-mail do remetente
    smtp_server = "smtp.hostinger.com"
    smtp_port = 587  # Porta TLS (pode usar 465 se for SSL)

    first_name = full_name.split()[0]
    subject = "Código de Rastreamento da Sua Compra"

    # Template HTML do e-mail
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #0072c6;
                color: white;
                padding: 10px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .body {{
                padding: 20px;
                color: #333333;
                line-height: 1.6;
            }}
            .footer {{
                padding: 10px;
                font-size: 12px;
                text-align: center;
                color: #888888;
            }}
            .tracking-code {{
                font-weight: bold;
                color: #0072c6;
                font-size: 18px;
            }}
            .button {{
                display: inline-block;
                background-color: #0072c6;
                color: white;
                padding: 10px 20px;
                margin-top: 20px;
                text-decoration: none;
                border-radius: 4px;
                font-size: 16px;
            }}
            .button:hover {{
                background-color: #005b9e;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Rastreamento de Pedido</h1>
            </div>
            <div class="body">
                <p>Olá {first_name},</p>
                <p>Sua compra foi registrada com sucesso! Aqui está o seu código de rastreamento:</p>
                <p class="tracking-code">{tracking_code}</p>
                <p>Você pode rastrear seu pedido clicando no botão abaixo:</p>
                <a href="https://correios-nine.vercel.app" class="button">Rastrear Pedido</a>
            </div>
            <div class="footer">
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Construindo o e-mail
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adicionando o corpo HTML ao e-mail
    msg.attach(MIMEText(html_template, 'html'))

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
        response = requests.post('https://correios-db-yiji.onrender.com/webhook', json=data)
        print(f"Response status: {response.status_code}, Response content: {response.content.decode()}")

        if response.status_code != 200:
            return jsonify({'status': 'error', 'message': 'Falha ao gerar código de rastreamento'}), 500

        tracking_data = response.json()
        tracking_code = tracking_data.get('code')

        if tracking_code:
            # Enviando o e-mail para o cliente com o código de rastreamento
            enviar_email(email, full_name, tracking_code)
            return jsonify({'status': 'success', 'message': 'E-mail enviado com sucesso'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Código de rastreamento não encontrado'}), 500

    except Exception as e:
        print(f"Erro no processamento do webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True)