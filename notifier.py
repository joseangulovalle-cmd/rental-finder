"""
Sistema de notificaciones por email
Envia un correo cuando aparecen propiedades nuevas
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import NOTIFY_EMAILS, SCHOOL_NAME


def send_notification(new_listings):
    """Envia email con las propiedades nuevas encontradas."""

    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_password:
        print("[Email] Credenciales no configuradas. Saltando notificacion.")
        return

    if not new_listings:
        print("[Email] No hay propiedades nuevas. No se envia correo.")
        return

    subject = f"🏠 {len(new_listings)} nueva(s) propiedad(es) cerca de {SCHOOL_NAME}"

    # Construir el cuerpo del email en HTML
    cards_html = ""
    for lst in new_listings:
        distance_text = f"{lst['distance_km']} km del colegio" if lst.get("distance_km") else "Distancia no disponible"
        image_html = f'<img src="{lst["image_url"]}" style="width:100%;height:180px;object-fit:cover;border-radius:8px 8px 0 0;" />' if lst.get("image_url") else ""
        cards_html += f"""
        <div style="border:1px solid #ddd;border-radius:10px;margin-bottom:20px;overflow:hidden;font-family:Arial,sans-serif;">
            {image_html}
            <div style="padding:16px;">
                <span style="background:#2563eb;color:white;padding:3px 10px;border-radius:20px;font-size:12px;">{lst['source']}</span>
                <h3 style="margin:10px 0 5px;font-size:16px;">{lst['title']}</h3>
                <p style="font-size:22px;font-weight:bold;color:#16a34a;margin:0 0 8px;">{lst['price']}</p>
                <p style="color:#666;margin:0 0 5px;font-size:14px;">📍 {lst['location']}</p>
                <p style="color:#666;margin:0 0 12px;font-size:14px;">🚶 {distance_text}</p>
                <a href="{lst['listing_url']}" style="background:#2563eb;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-size:14px;">
                    Ver anuncio →
                </a>
            </div>
        </div>
        """

    web_url = "https://joseangulovalle-cmd.github.io/rental-finder"

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <h2 style="color:#1e3a5f;">🏠 Nuevas propiedades encontradas</h2>
        <p style="color:#555;">
            Encontramos <strong>{len(new_listings)} propiedad(es) nueva(s)</strong>
            cerca de <strong>{SCHOOL_NAME}</strong>.
        </p>
        <div style="text-align:center;margin:20px 0;">
            <a href="{web_url}"
               style="background:#2563eb;color:white;padding:14px 32px;border-radius:8px;
                      text-decoration:none;font-size:16px;font-weight:bold;display:inline-block;">
                Ver todas las propiedades →
            </a>
        </div>
        {cards_html}
        <hr style="margin-top:30px;" />
        <p style="color:#aaa;font-size:12px;">
            Este correo fue enviado automaticamente por tu buscador de arriendos.<br/>
            Para ver todas las propiedades, visita tu pagina web.
        </p>
    </body></html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = ", ".join(NOTIFY_EMAILS)
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, NOTIFY_EMAILS, msg.as_string())

        print(f"[Email] Notificacion enviada a: {', '.join(NOTIFY_EMAILS)}")

    except Exception as e:
        print(f"[Email] Error al enviar: {e}")
