import time
import requests
import json
import random
import os
#import spacy
import logging
import re
import nltk
from nltk.stem import PorterStemmer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)
import undetected_chromedriver as uc  
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Constants
OPENROUTER_API_KEY = ""

YOUR_SITE_URL = "AIBrainL.ink"
YOUR_APP_NAME = "Reddit Scraper with AI Comments"

PERSONAS = {
    "teenager": "Respond as a texting teenager with lots of spelling mistakes, grammatical errors, run-on sentences, capitalization issues, and punctuation problems.",
    "normal": "Respond as a normal person on Reddit, with occasional spelling mistakes, grammatical errors, or run-on sentences.",
    "educated": "Respond as an educated person with very rare spelling mistakes.",
    "bot": "Respond with perfect spelling, grammar, and punctuation, like a bot would.",
}

SORT_TYPES = ["hot", "new", "top", "rising"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Load the English model (do this at the beginning of your script)
#nlp = spacy.load("en_core_web_md")
nltk.download('punkt_tab', quiet=True)

# def semantic_similarity(keywords, title, threshold=0.5, sleep_time=1):
#     if nlp is None:
#         custom_print("spaCy model not loaded. Skipping semantic similarity check.")
#         return False

#     try:
        
#         title_doc = nlp(title)
#         for keyword in keywords:
#             try:
#                 time.sleep(sleep_time / 3)
#                 keyword_doc = nlp(keyword)
#                 time.sleep(sleep_time / 3)
#                 similarity = title_doc.similarity(keyword_doc)
#                 time.sleep(sleep_time / 3)
#                 custom_print(f"Similarity between '{keyword}' and '{title}': {similarity}")
#                 logger.info(f"Similarity between '{keyword}' and '{title}': {similarity}")
                
#                 if similarity >= threshold:
#                     return True
#             except ValueError as e:
#                 custom_print(f"Error processing keyword '{keyword}': {str(e)}")
#                 logger.info(f"Error processing keyword '{keyword}': {str(e)}")
#                 continue
#     except Exception as e:
#         custom_print(f"Error in semantic_similarity function: {str(e)}")
#         logger.info(f"Error in semantic_similarity function: {str(e)}")
#         return False

#     return False

# Initialize the Porter Stemmer
ps = PorterStemmer()

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove apostrophes
    text = text.replace("'", "")
    # Remove non-alphanumeric characters and replace with space
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    # Stem the tokens
    stemmed_tokens = [ps.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def simple_semantic_similarity(keywords, title):
    try:
        # Preprocess the title
        processed_title = preprocess_text(title)
        
        # Preprocess and stem each keyword
        processed_keywords = [preprocess_text(keyword) for keyword in keywords]
        
        # Check if any processed keyword is in the processed title
        for keyword in processed_keywords:
            if keyword in processed_title:
                custom_print(f"Keyword '{keyword}' found in title: '{title}'")
                return True
        
        custom_print(f"No keywords found in title: '{title}'")
        return False

    except Exception as e:
        custom_print(f"Error in simple_semantic_similarity function: {str(e)}")
        return False

    

custom_print_function = print

def set_print_function(func):
    global custom_print_function
    custom_print_function = func

def custom_print(*args, **kwargs):
    global custom_print_function
    custom_print_function(*args, **kwargs)

def create_header_extension(headers):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Custom Header Modifier",
        "permissions": [
            "webRequest",
            "webRequestBlocking",
            "<all_urls>"
        ],
        "background": {
            "scripts": ["background.js"],
            "persistent": true
        }
    }
    """
    
    background_js = """
    var headers = %s;
    chrome.webRequest.onBeforeSendHeaders.addListener(
        function(details) {
            for (var header of headers) {
                var name = header.split(': ')[0];
                var value = header.split(': ')[1];
                var found = false;
                for (var i = 0; i < details.requestHeaders.length; ++i) {
                    if (details.requestHeaders[i].name.toLowerCase() === name.toLowerCase()) {
                        details.requestHeaders[i].value = value;
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    details.requestHeaders.push({name: name, value: value});
                }
            }
            return {requestHeaders: details.requestHeaders};
        },
        {urls: ["<all_urls>"]},
        ["blocking", "requestHeaders"]
    );
    """ % json.dumps(headers)

    extension_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "header_extension")
    os.makedirs(extension_dir, exist_ok=True)
    
    with open(os.path.join(extension_dir, "manifest.json"), "w") as f:
        f.write(manifest_json)
    
    with open(os.path.join(extension_dir, "background.js"), "w") as f:
        f.write(background_js)
    
    return extension_dir

def create_js_override_script(js_attributes):
    script = """
    (function() {
        var overrides = %s;
        
        function applyOverrides() {
            for (var key in overrides) {
                try {
                    var parts = key.split('.');
                    var obj = window;
                    for (var i = 0; i < parts.length - 1; i++) {
                        if (!(parts[i] in obj)) obj[parts[i]] = {};
                        obj = obj[parts[i]];
                    }
                    var propName = parts[parts.length - 1];
                    var propValue = overrides[key];

                    // Special handling for certain properties
                    if (key === 'navigator.userAgent') {
                        Object.defineProperty(navigator, 'userAgent', {get: function() { return propValue; }});
                    } else if (key === 'navigator.languages') {
                        Object.defineProperty(navigator, 'languages', {get: function() { return JSON.parse(propValue); }});
                    } else if (key.startsWith('navigator.') || key.startsWith('screen.')) {
                        // For navigator and screen properties, use Object.defineProperty
                        Object.defineProperty(obj, propName, {
                            get: function() { return propValue; },
                            configurable: true
                        });
                    } else {
                        // For other properties, try direct assignment
                        obj[propName] = propValue;
                    }
                } catch (e) {
                    console.error('Failed to set ' + key + ': ' + e.message);
                }
            }
        }

        applyOverrides();
        
        // Reapply overrides when a new document is loaded in any frame
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'IFRAME') {
                            node.addEventListener('load', function() {
                                try {
                                    applyOverrides.call(node.contentWindow);
                                } catch (e) {
                                    console.error('Failed to apply overrides to iframe:', e);
                                }
                            });
                        }
                    });
                }
            });
        });
        
        observer.observe(document, { childList: true, subtree: true });
    })();
    """ % json.dumps(dict(attr.split(': ', 1) for attr in js_attributes))
    return script

def verify_fingerprint_persistence(driver, fingerprint_settings):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:blank")
    
    # Check JavaScript attributes
    for attr in fingerprint_settings.get("js_attributes", []):
        name, expected_value = attr.split(': ', 1)
        actual_value = driver.execute_script(f"return {name};")
        if str(actual_value) != expected_value:
            custom_print(f"Warning: JavaScript attribute {name} does not match. Expected {expected_value}, got {actual_value}")
    
    # Check headers (this is tricky and might require visiting a test page)
    custom_print("Remember to manually verify header persistence by visiting a fingerprinting test site in a new tab")
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        custom_print(f"Timeout waiting for element: {value}")
        return None

def extract_comments(driver, url, max_comments, scroll_retries, button_retries):
    custom_print(f"Extracting comments from: {url}")
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    custom_print("Navigated to post page")

    comments = []
    try:
        custom_print("Waiting for comments to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "shreddit-comment"))
        )
        custom_print("Comments loaded successfully")

        last_comment_count = 0
        consecutive_same_count = 0

        while len(comments) < max_comments and consecutive_same_count < scroll_retries:
            # Try to click the "View more comments" button if it exists
            for _ in range(button_retries):
                try:
                    load_more_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'View more comments')]"))
                    )
                    driver.execute_script("arguments[0].click();", load_more_button)
                    custom_print("Clicked 'View more comments' button")
                    
                    break
                except TimeoutException:
                    custom_print("No 'View more comments' button found or not clickable")
            
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "shreddit-comment")
            
            for element in comment_elements[len(comments):]:
                try:
                    comment_text = element.find_element(By.CSS_SELECTOR, "div[slot='comment'] p").text.strip()
                    author = element.get_attribute("author")
                    depth = int(element.get_attribute("depth"))
                    parent_id = element.get_attribute("parentid")
                    aria_label = element.get_attribute("arialabel")
                    time_element = element.find_element(By.CSS_SELECTOR, "faceplate-timeago time")
                    time_ago = time_element.text.strip()

                    if "thread level" in aria_label:
                        comment_info = f"Comment thread level {depth}: Reply from {author}"
                    else:
                        comment_info = f"Comment from {author}"

                    comments.append({
                        "text": comment_text,
                        "author": author,
                        "depth": depth,
                        "parent_id": parent_id,
                        "comment_info": comment_info,
                        "time_ago": time_ago
                    })

                    custom_print(f"Extracted comment {len(comments)}: {comment_info} - {time_ago}")
                    custom_print(f"Comment text: {comment_text}")

                    if len(comments) >= max_comments:
                        break

                except NoSuchElementException:
                    custom_print(f"Skipping comment due to missing elements")
                except Exception as e:
                    custom_print(f"Error extracting comment: {str(e)}")

            if len(comments) == last_comment_count:
                consecutive_same_count += 1
            else:
                consecutive_same_count = 0

            last_comment_count = len(comments)

            if len(comments) < max_comments and consecutive_same_count < scroll_retries:
                custom_print("Scrolling down to load more comments...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new comments to load

        if len(comments) < max_comments:
            custom_print(f"Could only find {len(comments)} comments. There may not be {max_comments} comments available.")
        else:
            custom_print(f"Successfully extracted {len(comments)} comments.")

    except TimeoutException:
        custom_print("Timeout waiting for comments to load. Proceeding with available comments.")
    except Exception as e:
        custom_print(f"An error occurred while extracting comments: {str(e)}")
    finally:
        custom_print("Closing comment extraction window")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return comments

def generate_ai_comment(title, persona, ai_response_length=0, openrouter_api_key=None, custom_model=None, custom_prompt=None, product_keywords=None, website_address=None):
    custom_print("Generating AI comment...")
    
    # Default API key (replace with your actual default key)
    DEFAULT_API_KEY = "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"
    
    length_instruction = f"Generate a response that is approximately {ai_response_length} words long. " if ai_response_length > 0 else ""
    
    if custom_prompt and custom_prompt.strip():
        prompt = custom_prompt.format(
            title=title,
            length=length_instruction,
            product=product_keywords or "",
            website=website_address or ""
        )
    else:
        prompt = f"{PERSONAS[persona]} {length_instruction}Based on the following article title, generate an appropriate and insightful comment response. "
        if product_keywords:
            prompt += f"Incorporate information about this product: {product_keywords}. "
        if website_address:
            prompt += f"Include this website in your response: {website_address}. "
        prompt += f"\n\nTitle: {title}\n"

    prompt += "\nGenerated comment:"

    #custom_print(f"Sending request to AI model with prompt length: {len(prompt)} characters")
    #return "HERE IS AI COMMENT"
    try:
        # Use the provided API key if it's not blank, otherwise use the default
        api_key = openrouter_api_key.strip() if openrouter_api_key and openrouter_api_key.strip() else DEFAULT_API_KEY
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": YOUR_SITE_URL,
            "X-Title": YOUR_APP_NAME,
        }
        
        payload = {
            "model": custom_model or "google/gemma-2-9b-it:free",
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
       
        response.raise_for_status()
        ai_comment = response.json()["choices"][0]["message"]["content"]
        custom_print("AI comment generated successfully")
        custom_print(f"Generated comment: {ai_comment}")
        return ai_comment
    except requests.exceptions.RequestException as e:
        custom_print(f"Error making request to OpenRouter API: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            custom_print(f"Response status code: {e.response.status_code}")
            custom_print(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        custom_print(f"Unexpected error generating AI comment: {str(e)}")
        return None


def post_comment(driver, ai_comment, post_url):
    
    custom_print(f"Attempting to post comment to URL: {post_url}")
    
    if not post_url:
        custom_print("Error: post_url is None or empty")
        return False

    try:
        # Extract post ID from URL
        post_id = post_url.split("/")[-3]
        custom_print(f"Extracted postid: {post_id}")

        # Get CSRF token from cookie
        csrf_token = driver.get_cookie("csrf_token")
        if not csrf_token:
            custom_print("Error: CSRF token not found in cookies")
            return False
        csrf_token = csrf_token["value"]
        
        # Prepare headers matching the browser request
        headers = {
            "accept": "text/vnd.reddit.partial+html, application/json",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "Referer": post_url,
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        # Prepare the comment content in the exact format Reddit expects
        comment_content = {
            "document": [{
                "e": "par",
                "c": [{
                    "e": "text",
                    "t": ai_comment,
                    "f": [[0, 0, len(ai_comment)]]
                }]
            }]
        }

        # Prepare the form data
        form_data = {
            "content": json.dumps(comment_content),
            "mode": "richText",
            "richTextMedia": "[]",
            "csrf_token": csrf_token
        }

        # Get all cookies from the driver
        cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}

        # Make the POST request
        response = requests.post(
            f"https://www.reddit.com/svc/shreddit/t3_{post_id}/create-comment",
            headers=headers,
            cookies=cookies,
            data=form_data
        )

        # Check response
        if response.status_code == 200:
            custom_print("Comment posted successfully")
            return True
        else:
            custom_print(f"Failed to post comment. Status code: {response.status_code}")
            custom_print(f"Response content: {response.text}")
            return False

    except Exception as e:
        custom_print(f"Error in post_comment: {str(e)}")
        return False
    
#def post_comment(driver, ai_comment, post_url):
    custom_print(f"Attempting to post the AI-generated comment to URL: {post_url}")
    
    if not post_url:
        custom_print("Error: post_url is None or empty")
        return False

    try:
        # Extract post ID from URL
        post_id = post_url.split("/")[-3]
        custom_print(f"Extracted postid: {post_id}")

        # Get CSRF token from cookie
        csrf_token = driver.get_cookie("csrf_token")
        if not csrf_token:
            custom_print("Error: CSRF token not found in cookies")
            return False
        csrf_token = csrf_token["value"]
        custom_print(f"CSRF Token: {csrf_token}")

        # Prepare the comment data
        comment_data = {
            "content": json.dumps(
                {
                    "document": [
                        {
                            "e": "par",
                            "c": [
                                {
                                    "e": "text",
                                    "t": ai_comment,
                                    "f": [[0, 0, len(ai_comment)]],
                                }
                            ],
                        }
                    ]
                }
            ),
            "mode": "richText",
            "richTextMedia": json.dumps([]),
            "csrf_token": csrf_token,
        }

        # Set up the request headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Get all cookies from the driver
        cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
        
        custom_print("Comment data and headers prepared successfully")
        
        # For testing purposes, we'll just return True here
        # Make the POST request
        response = requests.post(
            f"https://www.reddit.com/svc/shreddit/t3_{post_id}/create-comment",
            headers=headers,
            cookies=cookies,
            data=comment_data,
        )

        custom_print(f"Response status: {response.status_code}")
        if response.status_code == 200:
         return True
        else:
         return False
        # In a real scenario, you would make the POST request here
        custom_print("Comment would be posted here in a real scenario")
        return True

    except Exception as e:
        custom_print(f"Error in post_comment: {str(e)}")
        return False


def login_and_scrape_reddit(
    username,
    password,
    subreddits,
    sort_type,
    max_articles,
    max_comments,
    min_wait_time,
    max_wait_time,
    custom_headers,
    ai_response_length,
    proxy_settings,
    fingerprint_settings,
    do_not_post,
    openrouter_api_key,
    scroll_retries,
    button_retries,
    persona,
    custom_model,
    custom_prompt,
    product_keywords,
    website_address,
    similarity_threshold,  
    similarity_method,
    tensorflow_sleep_time,
    existing_driver=None,
):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    
    #chrome_options = Options()
    #chrome_options.add_argument("--start-maximized")

    #service = Service(ChromeDriverManager().install())
    #driver = webdriver.Chrome(service=service, options=chrome_options)
    if existing_driver:
        driver = existing_driver
        custom_print("Using existing WebDriver session")
        
    else:
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        
        # Apply proxy settings
        if proxy_settings.get("enabled", False):
            proxy_string = f"{proxy_settings['type'].lower()}://{proxy_settings['host']}:{proxy_settings['port']}"
            options.add_argument(f'--proxy-server={proxy_string}')
            if proxy_settings.get("username") and proxy_settings.get("password"):
                options.add_argument(f"--proxy-auth={proxy_settings['username']}:{proxy_settings['password']}")

        # Explicitly specify Chrome version to match the installed version
        driver = uc.Chrome(
            options=options,
            version_main=133  # Set to match your Chrome version 133.0.6943.142
        )
        custom_print("New WebDriver session initialized")

        # Apply JavaScript attributes using CDP
        if fingerprint_settings.get("enabled", False):
            js_attributes = fingerprint_settings.get("js_attributes", [])
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": create_js_override_script(js_attributes)
            })
            
            # Verify persistence
            verify_fingerprint_persistence(driver, fingerprint_settings)
        custom_print("Navigating to Reddit login page...")
        driver.get("https://www.reddit.com/login")
              
        custom_print("Waiting for username field...")
        #username_field = wait_for_element(driver, By.ID, "login-username")
        username_field = WebDriverWait(driver, 999).until(
                EC.presence_of_element_located((By.ID, "login-username"))
            )
        custom_print("Waiting for password field...")
        #password_field = wait_for_element(driver, By.ID, "login-password")
        password_field = WebDriverWait(driver, 999).until(
                EC.presence_of_element_located((By.ID, "login-password"))
            )
        if username_field and password_field:
            custom_print("Entering username and password...")
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            custom_print("Logging in.. Waiting for articles to load...")

    custom_print("WebDriver initialized successfully")

    all_collected_info = []  # To store results from all subreddits

    try:
        custom_print(f"username:{username}                      \n subreddits:{subreddits}                     \n sort-type:{sort_type}                     \n max_articles:{max_articles}                     \n max_comments:{max_comments}                     \n min_wait_time:{min_wait_time}                     \n max_wait_time:{max_wait_time}                     \n Ai response length:{ai_response_length}                     \n proxy settings:{proxy_settings}                     \n openrouter api key:{openrouter_api_key} \n fingerprint settings: {fingerprint_settings}  \n comment scroll retries: {scroll_retries} \n comment button retries: {button_retries}                     \n persona:{persona}                     \n custom model:{custom_model}                     \n product keywords:{product_keywords}                     \n website:{website_address}                     \n similarity method:{similarity_method}                     \n similarity threshold:{similarity_threshold}                     \n tensorflow sleep time:{tensorflow_sleep_time}")                    
        

        
            
        try:
                #WebDriverWait(driver, 240).until(
                #EC.presence_of_element_located((By.CSS_SELECTOR, "shreddit-post"))
                #)
                wait_for_element(driver, By.CSS_SELECTOR, "shreddit-post")
                custom_print("Logged in. Articles loaded successfully")
        except TimeoutException:
                custom_print("Timeout waiting for login.")
                custom_print("Closing WebDriver...")
                driver.quit()
                return []

        for subreddit in subreddits:
            custom_print(f"\nStarting to scrape subreddit: r/{subreddit}")
            subreddit_url = f"https://www.reddit.com/r/{subreddit}/{sort_type}/"
            driver.get(subreddit_url)
            custom_print("Waiting for page to load...")
            
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            custom_print("Articles loaded.")

            collected_info = []
            articles_scraped = 0
            last_height = driver.execute_script("return document.body.scrollHeight")
            processed_urls = set()
            no_new_posts_count = 0


            # Split product keywords into keywords
            if isinstance(product_keywords, str):
                product_keywords = [kw.strip().lower() for kw in product_keywords.split(',')]
            elif isinstance(product_keywords, list):
                product_keywords = [kw.strip().lower() for kw in product_keywords]
            else:
                custom_print("Error: product_keywords is neither a string nor a list")
                product_keywords = []

            while articles_scraped < max_articles:
                custom_print("Finding posts...")
                posts = driver.find_elements(By.TAG_NAME, "article")
                custom_print(f"Found {len(posts)} posts")

                new_posts_processed = False
                for post in posts:
                    if articles_scraped >= max_articles:
                        break
                    
                    try:
                        shreddit_post = post.find_element(By.TAG_NAME, "shreddit-post")
                        url = "https://www.reddit.com" + shreddit_post.get_attribute("permalink")

                        if url in processed_urls:
                            continue

                        custom_print(f"Processing post {articles_scraped + 1}...")
                        title = post.get_attribute("aria-label")

                        custom_print(f"Post {articles_scraped + 1}/{max_articles} - Title: {title}")
                        custom_print(f"Post {articles_scraped + 1}/{max_articles} - URL: {url}")
                        time.sleep(button_retries)
                        # Check if the title contains any of the product keywords
                        title = title.lower()
                        
                        if similarity_method == "TensorFlow (semantic_similarity)":
                            is_relevant = semantic_similarity(product_keywords, title, threshold=similarity_threshold, sleep_time=tensorflow_sleep_time)
                        else:  # "Simple (simple_semantic_similarity)"
                            is_relevant = simple_semantic_similarity(product_keywords, title)

                        if is_relevant:
                            custom_print(f"Relevant content found in post {articles_scraped + 1}")

                            comments = []
                            if max_comments > 0:
                                custom_print(f"Extracting up to {max_comments} comments...")
                                comments = extract_comments(driver, url, max_comments, scroll_retries, button_retries)
                                custom_print(f"Extracted {len(comments)} comments")

                            custom_print(f"Generating AI comment for post {articles_scraped + 1}...")
                            ai_comment = generate_ai_comment(
                                title,
                                persona,
                                ai_response_length,
                                openrouter_api_key,
                                custom_model,
                                custom_prompt,
                                product_keywords,
                                website_address
                            )

                            collected_info.append({
                                "subreddit": subreddit,
                                "title": title,
                                "url": url,
                                "comments": comments,
                                "ai_comment": ai_comment,
                            })
                           
                        else:
                            custom_print(f"No relevant keywords found in post {articles_scraped + 1}. Skipping...")

                        processed_urls.add(url)
                        articles_scraped += 1
                        new_posts_processed = True

                    except StaleElementReferenceException:
                        custom_print(f"Stale element reference for post {articles_scraped + 1}. Skipping...")
                    except NoSuchElementException as e:
                        custom_print(f"Element not found for post {articles_scraped + 1}: {str(e)}. Skipping...")
                    except Exception as e:
                        custom_print(f"An error occurred processing post {articles_scraped + 1}: {str(e)}. Skipping...")

                custom_print(f"Processed {articles_scraped} posts so far")

                if not new_posts_processed:
                    no_new_posts_count += 1
                    custom_print(f"No new posts found. Scroll attempt {no_new_posts_count}/{scroll_retries}")
                    if no_new_posts_count >= scroll_retries:
                        custom_print(f"No new posts found after {scroll_retries} scrolls. Moving to next subreddit.")
                        break
                else:
                    no_new_posts_count = 0  # Reset the counter if new posts were processed

                # Scroll down to load more content
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new content to load
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_new_posts_count += 1
                    custom_print(f"Page height didn't change. Scroll attempt {no_new_posts_count}/{scroll_retries}")
                    if no_new_posts_count >= scroll_retries:
                        custom_print("No more posts to load after multiple scroll attempts.")
                        break
                else:
                    custom_print("Scrolled successfully, new content loaded.")
                    no_new_posts_count = 0  # Reset the counter if the page height changed

            all_collected_info.extend(collected_info)
            custom_print(f"Scraping completed for r/{subreddit}. Total relevant posts processed: {len(collected_info)}")

    except Exception as e:
        custom_print(f"An unexpected error occurred: {str(e)}")
    finally:
        custom_print("Scraping process completed.")

    custom_print(f"Scraping completed for all subreddits. Total relevant posts processed: {len(all_collected_info)}")
    return all_collected_info, driver

if __name__ == "__main__":
    # This block can be used for testing the script directly
    pass
