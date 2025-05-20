import logging
import smtplib, ssl 
from pathlib import Path
from email import encoders
from email.utils import formataddr
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class Smtp:
    def __init__(self, email, senha):
        self.EMAIL = email
        self.SENHA = senha
        self.CONTEXT = ssl.create_default_context()
        self.logger = logging.getLogger(__name__)

    def adicionar_anexo(self, msg, anexo, i):
        try:
            with open(anexo, 'rb') as arquivo:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(arquivo.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition', 
                    f'attachment; filename="anexo{i}{anexo.suffix}"'
                )

                msg.attach(part)

        except Exception as e:
            self.logger.error(f'Erro ao anexar arquivo {anexo}: {e}')

    def enviar_email(self, destinatario, encaminhado, anexo):
        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr(('TatySMTPDocs', self.EMAIL)) # Remetente
            msg['To'] = destinatario
            msg['Cc'] = encaminhado
            msg['Subject'] = (anexo.stem if Path(anexo).is_file() else anexo.name).replace('_', '/') # Assunto

            # Adiciona anexo
            if Path(anexo).is_file():
               self.adicionar_anexo(msg, anexo, '')
            else: # Se o arquivo for uma pasta, os arquivos dentro dele são enviados juntos
                num = 0
                for arquivo in Path(anexo).iterdir(): 
                    if arquivo.is_file():
                        self.adicionar_anexo(msg, arquivo, num)
                        num += 1

            # Envio do e-mail
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                # server.set_debuglevel(1)
                server.starttls(context=self.CONTEXT)
                server.login(self.EMAIL, self.SENHA)
                server.sendmail(self.EMAIL, [destinatario, encaminhado], msg.as_string())
            
            logging.info(f'Email enviado para {destinatario} com o anexo: {anexo.name}')

            return True
        
        except smtplib.SMTPAuthenticationError:
            self.logger.error("Falha na autenticação SMTP. Verifique e-mail e senha.")
            return False
        
        except Exception as e:
            self.logger.error(f'Erro ao enviar email para {destinatario}: {e}')
            return False