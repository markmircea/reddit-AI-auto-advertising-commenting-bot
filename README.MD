![redditbot](https://github.com/user-attachments/assets/662a75ab-c373-44b3-93f8-bf9cd4e7afbe)
# Reddit AI Commenter Pro

Reddit AI Commenter Pro is a Python application that scrapes Reddit posts, generates AI comments, and allows for review and posting of these comments.

## File Structure

- `reddit_scraper_gui.py`: Main application file with the GUI
- `gui_components.py`: GUI-related classes and dialogs
- `scraper.py`: Main scraping functionality
- `utils.py`: Utility functions and constants
- `styles.py`: Styling and visual aspects

Note: If you see a `reddit_scraper.py` file in your directory, it's from the old version and can be safely removed.

## Setup and Installation

1. **Install Python**
   - Download and install Python 3.8 or later from [python.org](https://www.python.org/downloads/)
   - Ensure you check "Add Python to PATH" during installation

2. **Set up a virtual environment (recommended)**
   - Open a terminal or command prompt
   - Navigate to the project directory
   - Create a virtual environment:
     ```
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows:
       ```
       venv\Scripts\activate
       ```
     - On macOS and Linux:
       ```
       source venv/bin/activate
       ```

3. **Install dependencies**
   - With the virtual environment activated, run:
     ```
     pip install -r requirements.txt
     ```
   - Install spaCy language model:
     ```
     python -m spacy download en_core_web_md
     ```

4. **Configure settings**
   - Open `reddit_scraper_gui.py` and update any default settings if needed

## Running the Application

1. Ensure your virtual environment is activated
2. Run the following command:
   ```
   python reddit_scraper_gui.py
   ```

## Usage

1. Enter your Reddit username and password
2. Add subreddits you want to scrape
3. Configure scraping settings (max articles, comments, etc.)
4. Click "Start Scraping, Generating and Reviewing Comments"
5. Review and select AI-generated comments
6. The application will post selected comments to Reddit

## Additional Notes

- Make sure you comply with Reddit's terms of service and API usage guidelines
- Be cautious when using automated posting features to avoid potential account restrictions

## Troubleshooting

- If you encounter issues with TensorFlow, you can disable neural word vectors or increase the similarity threshold in the advanced settings
- For any crashes or errors, check the log file generated in the application directory

## Creating Requirements File

To update the requirements file with your current environment packages:

```
pip freeze > requirements.txt
```

Remember to deactivate your virtual environment when you're done:
```
deactivate
```

## License

[Include your license information here]
