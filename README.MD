# Guide: Running a Python Script on a New Computer

Follow these steps to run your Python script on a new computer:

1. **Install Python**
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - Ensure you check "Add Python to PATH" during installation

2. **Set up a virtual environment (recommended)**
   - Open a terminal or command prompt
   - Navigate to your project directory
   - Create a virtual environment:
     ```
     python -m venv myenv
     ```
   - Activate the virtual environment:
     - On Windows:
       ```
       myenv\Scripts\activate
       ```
     - On macOS and Linux:
       ```
       source myenv/bin/activate
       ```

3. **Install dependencies**
   - If you have a `requirements.txt` file:
     ```
     pip install -r requirements.txt
     ```
   - If not, install required packages individually:
     ```
     pip install package_name
     ```

4. **Transfer your script**
   - Copy your Python script file(s) to the new computer
   - Place them in your project directory

5. **Configure environment-specific settings**
   - Set any necessary environment variables
   - Update file paths in your script if needed

6. **Run the script**
   - In the terminal, with your virtual environment activated, run:
   ```
   .\venv\Scripts\activate
   ```
     ```
     python your_script.py
     ```

Remember to deactivate your virtual environment when you're done:
```
deactivate
```

This process ensures that your script runs in an isolated environment with all necessary dependencies, regardless of the system-wide Python setup on the new computer.

Create req text
pip freeze > requirements.txt
