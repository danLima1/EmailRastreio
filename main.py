from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

def enviar_email(to_email, full_name, tracking_code, numero_pedido, previsao_entrega):
    from_email = "suporte@fast-tracker.site"
    from_name = "Rastreamento"
    password = "Batata135-"
    smtp_server = "smtp.titan.email"
    smtp_port = 587

    nome_cliente = full_name
    data_envio = datetime.now().strftime('%d/%m/%Y')
    subject = "Código de Rastreio do seu Pedido"

    # Todas as chaves do CSS agora são {{ e }}
    # Placeholders de variáveis continuam com {}
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Código de Rastreio do seu Pedido</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .logo {{
                text-align: center;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}
            .logo svg {{
                width: 32px;
                height: 32px;
                color: #6a3de8;
            }}
            .logo-text {{
                color: #6a3de8;
                font-size: 28px;
                font-weight: bold;
                text-decoration: none;
            }}
            .container {{
                background-color: #f8f7ff;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                border: 1px solid #e6e3ff;
            }}
            .tracking-code {{
                background-color: #f0ebff;
                padding: 15px;
                border-radius: 5px;
                font-size: 18px;
                text-align: center;
                margin: 20px 0;
                border: 1px solid #d9d1ff;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #6a3de8;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
                transition: background-color 0.3s;
            }}
            .button:hover {{
                background-color: #5632c0;
            }}
            h2 {{
                color: #6a3de8;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
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
            
            <p>Ótimas notícias! Seu pedido já está em preparo.</p>
            
            <p>Aqui está seu código de rastreio:</p>
            
            <div class="tracking-code">
                <strong>{codigo_rastreio}</strong>
            </div>
            
            <p>Você pode acompanhar seu pedido clicando no botão abaixo:</p>
            
            <center>
                <a href="https://fasttracker.site/?code={codigo_rastreio}" class="button">Rastrear Pedido</a>
            </center>
            
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

    html_content = html_template.format(
        nome_cliente=nome_cliente,
        numero_pedido=numero_pedido,
        codigo_rastreio=tracking_code,
        data_envio=data_envio,
        previsao_entrega=previsao_entrega
    )

    msg = MIMEMultipart('alternative')
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"E-mail enviado para {to_email}.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook2():
    data = request.json
    customer = data.get('customer', {})
    email = customer.get('email')
    full_name = customer.get('name')

    if not email or not full_name:
        return jsonify({'status': 'error', 'message': 'Dados incompletos'}), 400

    try:
        # Enviar dados para o backend de rastreamento
        response = requests.post(
            'https://correios-db-yiji.onrender.com/webhook',
            json=data
        )
        print(f"Response status: {response.status_code}, Response content: {response.content.decode()}")

        # Verificar se a resposta foi bem-sucedida
        if response.status_code not in [200, 201]:
            return jsonify({'status': 'error', 'message': 'Falha ao gerar código de rastreamento'}), 500

        # Processar a resposta do backend de rastreamento
        tracking_data = response.json()
        tracking_code = tracking_data.get('code')
        previsao_entrega = tracking_data.get('previsao_entrega', 'Não disponível')
        numero_pedido = data.get('order_number', 'Indisponível')

        # Verificar se o código foi gerado
        if not tracking_code:
            print("Erro: Código de rastreamento não encontrado na resposta.")
            return jsonify({'status': 'error', 'message': 'Código de rastreamento não encontrado'}), 500

        # Enviar e-mail com os dados
        enviar_email(email, full_name, tracking_code, numero_pedido, previsao_entrega)
        return jsonify({'status': 'success', 'message': 'E-mail enviado com sucesso'}), 200

    except requests.exceptions.RequestException as e:
        print(f"Erro ao se comunicar com o backend de rastreamento: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Falha na comunicação com o backend de rastreamento'}), 500

    except Exception as e:
        print(f"Erro no processamento do webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True)
