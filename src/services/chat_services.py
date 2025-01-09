# src/services/chat_services.py

from datetime import datetime
from typing import Dict, List, Any
import google.generativeai as genai
# Updated imports for LangChain 0.2+
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
import logging
from ..utils.cache import cache

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.query_history = []
        self.llm = self._initialize_llm()
        self.toolkit = SQLDatabaseToolkit(db=self.db_manager.db, llm=self.llm)
        self.agent_executor = self._initialize_agent()

    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize the language model"""
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                convert_system_message_to_human=True,
                temperature=0.3
            )
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise

    # src/services/chat_services.py
    def _initialize_agent(self):
        """Initialize the SQL agent"""
        try:
            return create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                agent_kwargs={
                    "prefix": """You are a helpful SQL assistant that helps users understand their database. 
                    Always explain your thinking process and provide clear, concise responses."""
                },
                max_iterations=10,  # Add this line to increase iterations
                early_stopping_method="generate",  # Add this for better control
                handle_parsing_errors=True  # Add this for better error handling
            )
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise

        
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query and return the result
        """
        try:
            # Check cache first
            cache_key = f"query_{query}"
            if cache.has(cache_key):
                logger.info(f"Cache hit for query: {query[:50]}...")
                return cache.get(cache_key)

            # Process query
            start_time = datetime.now()
            result = self.agent_executor.run(query)
            execution_time = (datetime.now() - start_time).total_seconds()

            # Format response
            response = {
                "result": result,
                "execution_time": execution_time,
                "timestamp": self.get_timestamp()
            }

            # Store in history
            self._add_to_history(query, response)

            # Cache the result
            cache.set(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def _add_to_history(self, query: str, response: Dict[str, Any]):
        """Add query to history"""
        history_entry = {
            "query": query,
            "response": response,
            "timestamp": self.get_timestamp()
        }
        self.query_history.append(history_entry)
        if len(self.query_history) > 100:  # Keep only last 100 queries
            self.query_history.pop(0)

    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query history"""
        return self.query_history

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()

    def get_suggested_queries(self, context: str = None) -> List[str]:
        """Get suggested queries based on context and history"""
        suggested_queries = [
            "Show total sales by month",
            "Find top selling pizzas",
            "Calculate average order value",
            "Show peak ordering hours"
        ]
        return suggested_queries

    def get_query_analytics(self) -> Dict[str, Any]:
        """Get analytics about query patterns"""
        if not self.query_history:
            return {}

        return {
            "total_queries": len(self.query_history),
            "avg_execution_time": sum(q["response"]["execution_time"] for q in self.query_history) / len(self.query_history),
            "last_query_time": self.query_history[-1]["timestamp"]
        }