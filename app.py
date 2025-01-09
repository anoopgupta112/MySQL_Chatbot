from flask import Flask, jsonify, render_template, request, session
from src.services.chat_services import ChatService
from src.database.db_manager import DatabaseManager
from src.utils.security import require_api_key, sanitize_input
from src.utils.cache import cache
from config.settings import Config
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")

# Initialize services
db_manager = DatabaseManager(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME")
)

chat_service = ChatService(db_manager)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form["msg"]
        result = chat_service.process_query(msg)
        return str(result['result'])
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return str(f"Error: {str(e)}"), 500

@app.route("/api/query", methods=["POST"])
@require_api_key
@cache.memoize(timeout=300)  # Cache for 5 minutes
def process_query():
    try:
        data = request.get_json()
        query = sanitize_input(data.get('query', ''))
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Process the query
        result = chat_service.process_query(query)
        
        # Log the successful query
        logger.info(f"Successfully processed query: {query[:50]}...")
        
        return jsonify({
            "success": True,
            "data": {
                "result": result['result'],
                "sql": result.get('sql'),
                "visualization": result.get('visualization'),
                "query": query
            },
            "metadata": {
                "cached": cache.has(f"query_{query}"),
                "timestamp": chat_service.get_timestamp()
            }
        })

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/history", methods=["GET"])
@require_api_key
def get_history():
    try:
        history = chat_service.get_query_history()
        return jsonify({"success": True, "history": history})
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/tables", methods=["GET"])
@require_api_key
def get_tables():
    try:
        tables = db_manager.get_tables()
        return jsonify({"success": True, "tables": tables})
    except Exception as e:
        logger.error(f"Error fetching tables: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)