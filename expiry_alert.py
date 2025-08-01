import os
import logging
from datetime import datetime
from twilio.rest import Client
from config import Config
from db import get_expiring_items

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Twilio client
twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_expiry_alerts():
    """Send WhatsApp alerts for items expiring soon"""
    try:
        # Get items expiring within the configured days
        expiring_items = get_expiring_items(days=Config.EXPIRY_ALERT_DAYS)
        
        if not expiring_items:
            logger.info("No items expiring soon. No alerts sent.")
            return
        
        # Group items by shop owner
        shop_items = {}
        for item in expiring_items:
            owner_phone = item['shops']['owner_phone']
            if owner_phone not in shop_items:
                shop_items[owner_phone] = []
            shop_items[owner_phone].append(item)
        
        # Send alerts to each shop owner
        for owner_phone, items in shop_items.items():
            # Format the message
            message = f"⚠️ *EXPIRY ALERT* ⚠️\n\nThe following items in your shop will expire within {Config.EXPIRY_ALERT_DAYS} days:\n\n"
            
            for item in items:
                days_left = (datetime.strptime(item['expiry_date'], '%Y-%m-%d') - datetime.now()).days
                message += f"• {item['name']} - Expires in {days_left} days ({item['expiry_date']})\n"
            
            message += "\nConsider discounting these items or planning promotions to reduce waste."
            
            # Send WhatsApp message
            twilio_message = twilio_client.messages.create(
                from_=f'whatsapp:{Config.TWILIO_WHATSAPP_NUMBER}',
                body=message,
                to=f'whatsapp:{owner_phone}'
            )
            
            logger.info(f"Sent expiry alert to {owner_phone} (SID: {twilio_message.sid})")
        
        return True
    except Exception as e:
        logger.error(f"Error sending expiry alerts: {str(e)}")
        return False

def setup_cron_job():
    """Set up a cron job to run the expiry alert function daily"""
    try:
        from crontab import CronTab
        
        # Get the current user's crontab
        cron = CronTab(user=True)
        
        # Remove any existing jobs with the same comment
        for job in cron.find_comment('whatsapp_expiry_alert'):
            cron.remove(job)
        
        # Create a new job that runs daily at 9 AM
        job = cron.new(command=f'cd {os.getcwd()} && python -c "from expiry_alert import send_expiry_alerts; send_expiry_alerts()"')
        job.setall('0 9 * * *')  # Run at 9:00 AM every day
        job.set_comment('whatsapp_expiry_alert')
        
        # Write the crontab
        cron.write()
        
        logger.info("Cron job for expiry alerts set up successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up cron job: {str(e)}")
        return False

# For testing purposes
if __name__ == "__main__":
    send_expiry_alerts()