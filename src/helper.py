import os
from langchain.agents import *
from dotenv import load_dotenv
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI 
import google.generativeai as genai

KEY=os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=KEY)
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

# by passing args in this class we can chat with MySQL DB
class Chat_With_Sql:
    def __init__(self,db_user,db_password,db_host,db_name):
 
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_name = db_name
    
    def message(self,query):
        # connecting with db
        db = SQLDatabase.from_uri(f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}")
        # Intializing the toolkit
        toolkit = SQLDatabaseToolkit(db=db,llm=llm)
        # creatin the agent executor
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True
        )
         
        response = agent_executor.run(query)
        return response

# # execution of the query

# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
# db_host = os.getenv('DB_HOST')
# db_name = os.getenv('DB_NAME')
# obj = Chat_With_Sql(db_user,db_password,db_host, db_name)
# print(obj.message("Give me the distinct price of pizzas?"))


# # output [12.75, 16.75, 20.75, 12.0, 16.0, 20.5, 10.5, 13.25, 16.5, 11.0, 14.5, 17.5, 9.75, 12.5, 15.25, 25.5, 35.95, 23.65, 12.25, 16.25, 20.25, 15.5, 18.5, 11.75, 14.75, 17.95, 21.0]