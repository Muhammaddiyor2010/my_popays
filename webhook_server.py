from aiohttp import web, web_request
import json
import logging
from bot import process_order_data, process_contact_data
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_webhook(request: web_request.Request):
    """Handle webhook requests from web app"""
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {data}")
        
        # Process based on data type
        if data.get('type') == 'order':
            await process_order_data(data)
        elif data.get('type') == 'contact':
            await process_contact_data(data)
        else:
            logger.warning(f"Unknown data type: {data.get('type')}")
        
        return web.json_response({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)

async def health_check(request: web_request.Request):
    """Health check endpoint"""
    return web.json_response({'status': 'healthy'})

def create_app():
    """Create web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/health', health_check)
    
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080)
