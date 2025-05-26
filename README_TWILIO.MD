# Twilio API Integration Guide for Lu Estilo

## Overview

This guide explains how to integrate Twilio's WhatsApp API with Lu Estilo's backend system for sending automated messages to customers.

## Prerequisites

- Twilio Account
- WhatsApp Business Profile
- Twilio Auth Token and Account SID
- Python 3.11+
- FastAPI

## Setup

### 1. Environment Variables

Add these to your `.env` file:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number
```

### 2. Install Dependencies

Add to `requirements.txt`:

```
twilio==8.12.0
```

### 3. Code Implementation

```python
from twilio.rest import Client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize Twilio client
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

async def send_whatsapp_message(to_number: str, message: str) -> dict:
    """
    Send WhatsApp message using Twilio

    Args:
        to_number (str): Recipient's phone number with country code
        message (str): Message content

    Returns:
        dict: Response from Twilio API
    """
    try:
        message = client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            body=message,
            to=f"whatsapp:{to_number}"
        )
        return {
            "status": "success",
            "message_sid": message.sid,
            "to": to_number
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send WhatsApp message: {str(e)}"
        )
```

## Usage Examples

### 1. Order Confirmation

```python
async def send_order_confirmation(order_id: str, phone_number: str):
    message = f"""
    Thank you for your order #{order_id}!
    We'll notify you when it's ready for pickup.

    - Lu Estilo Team
    """
    return await send_whatsapp_message(phone_number, message)
```

### 2. Promotional Messages

```python
async def send_promotion(phone_number: str, discount: int):
    message = f"""
    Special Offer!
    Get {discount}% off on all items today.
    Visit Lu Estilo now!
    """
    return await send_whatsapp_message(phone_number, message)
```

### 3. Order Status Updates

```python
async def send_status_update(order_id: str, status: str, phone_number: str):
    message = f"""
    Order Update:
    Your order #{order_id} is now {status}.
    """
    return await send_whatsapp_message(phone_number, message)
```

## Best Practices

1. **Error Handling**

   - Always wrap Twilio API calls in try-except blocks
   - Log errors for debugging
   - Return meaningful error messages

2. **Rate Limiting**

   - Implement rate limiting for bulk messages
   - Use async queues for large campaigns

3. **Message Templates**

   - Use pre-approved message templates
   - Keep messages concise and clear
   - Include order/transaction references

4. **Phone Number Validation**
   - Validate phone numbers before sending
   - Ensure proper international format
   - Handle country codes correctly

## Testing

```python
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_send_whatsapp_message():
    with patch('twilio.rest.Client') as mock_client:
        mock_message = mock_client.return_value.messages.create
        mock_message.return_value.sid = "test_sid"

        result = await send_whatsapp_message(
            "+1234567890",
            "Test message"
        )

        assert result["status"] == "success"
        assert "message_sid" in result
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**

   - Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
   - Check environment variables are loaded correctly

2. **Message Not Delivered**

   - Verify recipient's number format
   - Check WhatsApp opt-in status
   - Review Twilio console for delivery status

3. **Rate Limiting**
   - Monitor message volume
   - Implement exponential backoff
   - Use queuing for bulk messages

### Debug Tips

1. Enable Twilio debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Monitor webhook responses:

```python
@app.post("/twilio/status")
async def message_status(status: dict):
    logging.info(f"Message status: {status}")
```

## Security Considerations

1. **API Key Protection**

   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys periodically

2. **Phone Number Privacy**

   - Hash/encrypt stored phone numbers
   - Limit access to phone number data
   - Implement proper data retention policies

3. **Message Content**
   - Sanitize user input
   - Avoid sending sensitive information
   - Follow WhatsApp's content policies

## Monitoring and Analytics

1. **Message Metrics**

   - Track delivery rates
   - Monitor engagement
   - Analyze response times

2. **Cost Tracking**

   - Monitor API usage
   - Track message volumes
   - Set up billing alerts

3. **Performance Monitoring**
   - Log API response times
   - Track error rates
   - Monitor queue lengths

## Compliance

1. **GDPR Compliance**

   - Get explicit consent
   - Provide opt-out mechanism
   - Document data processing

2. **WhatsApp Policy**
   - Follow message templates
   - Respect quiet hours
   - Maintain quality rating

## Support and Resources

- [Twilio Documentation](https://www.twilio.com/docs/whatsapp)
- [WhatsApp Business API](https://www.whatsapp.com/business/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## Updates and Maintenance

1. **Version Updates**

   - Keep dependencies updated
   - Monitor API changes
   - Test after updates

2. **Backup Plans**
   - Have fallback notification methods
   - Implement retry mechanisms
   - Maintain service redundancy
