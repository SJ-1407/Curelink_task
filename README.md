
# Curelink Task

## Setup Instructions

Follow the steps below to set up the Curelink application:

### 1. Create a Virtual Environment

To create a virtual environment, open your terminal or command prompt and run the following command:

    
        python -m venv venv
    

 ### 2. Activate the Virtual Environment
  On Windows:
            
        
          venv\Scripts\activate
          

  On macOS/Linux:
    
    
      source venv/bin/activate

### 3. Install Dependencies

To install the dependencies, run:

     pip install -r requirements.txt

### 4. Create a .env File
In your project directory, create a file named .env and add your API key for the Groq model (or any other LLM you wish to use) in the following format:
text
     
     GROQ_API_KEY=your_api_key_here

If you are using a different LLM, replace GROQ_API_KEY with the relevant key name and value.
### 5. Modify main.py
   Ensure that your main.py file correctly loads the API key from the .env file and initializes the model accordingly.
### 6. Run the Application
Once everything is set up, you can run the application by executing:
  
     python main.py
