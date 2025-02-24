***Backend Project Setup Instructions**
------------------------------------

This project provides a Python-based backend. Follow the steps below to set up your environment, configure AWS credentials for accessing Bedrock, and run the application.

1. **Create a Virtual Environment**
-------------------------------
Open your terminal and run the following command to create a virtual environment:

    python3 -m venv env

Activate the virtual environment:

    - On macOS/Linux:
          source env/bin/activate
    - On Windows:
          env\Scripts\activate

2. **Install Dependencies**
-----------------------
Install the required packages from requirements.txt:

    pip install -r requirements.txt

3. **Start Docker Services**
------------------------
Ensure Docker is installed and running. Start the necessary Docker containers with:

    docker-compose up -d

4. **Configure AWS Credentials for Bedrock**
------------------------------------------
To access AWS Bedrock services, configure your AWS credentials. You can add your AWS login details to an environment file (e.g., `.env`) or export them directly in your terminal session:

    AWS_ACCESS_KEY_ID=your_access_key_id
    AWS_SECRET_ACCESS_KEY=your_secret_access_key
    AWS_REGION=your_aws_region

5. **Run the Application**
----------------------
Start the backend application by executing:

    python3 app.py

**Note:** If your main application file has a different name, adjust the command accordingly.

**Additional Information:**
-----------------------
- **Deactivating the Virtual Environment:** When finished, you can deactivate the virtual environment with:
  
      deactivate

- **Troubleshooting:**
    - Ensure Docker is installed and running.
    - Verify that the virtual environment is activated before installing dependencies.