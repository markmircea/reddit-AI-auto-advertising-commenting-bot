import time
import requests
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)

# Constants
OPENROUTER_API_KEY = (
    "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"
)
YOUR_SITE_URL = "easyace.ai"
YOUR_APP_NAME = "Reddit Scraper with AI Comments"



PERSONAS = {
    "teenager": "Respond as a texting teenager with lots of spelling mistakes, grammatical errors, run-on sentences, capitalization issues, and punctuation problems.",
    "normal": "Respond as a normal person on Reddit, with occasional spelling mistakes, grammatical errors, or run-on sentences.",
    "educated": "Respond as an educated person with very rare spelling mistakes.",
    "bot": "Respond with perfect spelling, grammar, and punctuation, like a bot would.",
}

SORT_TYPES = ["hot", "new", "top", "rising"]

custom_print_function = print

def set_print_function(func):
    global custom_print_function
    custom_print_function = func

def custom_print(*args, **kwargs):
    global custom_print_function
    custom_print_function(*args, **kwargs)


def get_user_input(prompt, default, options=None):
    if options:
        custom_print(f"{prompt} Options: {', '.join(options)}")
    
    if default.lower() in ['yes', 'no']:
        default_char = 'y' if default.lower() == 'yes' else 'n'
        user_input = input(f"{prompt} (y/n, default: {default_char}): ").strip().lower()
        if user_input == '':
            return default.lower() == 'yes'
        elif user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            custom_print(f"Invalid input. Using default: {default}")
            return default.lower() == 'yes'
    else:
        user_input = input(f"{prompt} (default: {default}): ").strip().lower()
        if options and user_input and user_input not in options:
            custom_print(f"Invalid option. Using default: {default}")
            return default
        return user_input if user_input else default

def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        custom_print(f"Timeout waiting for element: {value}")
        return None


def extract_comments(driver, url, max_comments):
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

        comment_elements = driver.find_elements(By.CSS_SELECTOR, "shreddit-comment")
        custom_print(f"Found {len(comment_elements)} comments")

        for i, element in enumerate(comment_elements[:max_comments], 1):
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

                custom_print(f"Extracted comment {i}: {comment_info} - {time_ago}")
                custom_print(f"Comment text: {comment_text}")

            except NoSuchElementException:
                custom_print(f"Skipping comment {i} due to missing elements")
            except Exception as e:
                custom_print(f"Error extracting comment {i}: {str(e)}")

    except TimeoutException:
        custom_print("Timeout waiting for comments to load. Proceeding with available comments.")
    except Exception as e:
        custom_print(f"An error occurred while extracting comments: {str(e)}")
    finally:
        custom_print("Closing comment extraction window")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    custom_print(f"Extracted {len(comments)} comments in total")
    return comments

def generate_ai_comment(title, comments, persona, include_comments, ai_response_length=0):
    custom_print("Generating AI comment...")
    
    length_instruction = f"Generate a response that is approximately {ai_response_length} words long. " if ai_response_length > 0 else ""
    
    if include_comments:
        prompt = f"{PERSONAS[persona]} {length_instruction}Based on the following article title and existing comments, generate an appropriate and insightful comment response to the article title. DO NOT INTERACT WITH THE OTHER EXISTING COMMENTS IN ANY WAY, ONLY RESPOND TO THE TITLE! Use the existing comments to determine an appropriate length for your answer, if they have short answers, so should you. :\n\nTitle: {title}\n\nExisting comments:\n"

        for comment in comments:
            indent = "  " * comment["depth"]
            prompt += f"{indent}{comment['comment_info']} - {comment['time_ago']}:\n{indent}{comment['text']}\n\n"
    else:
        prompt = f"{PERSONAS[persona]} {length_instruction}Based on the following article title, generate an appropriate and insightful comment response. :\n\nTitle: {title}\n"

    prompt += "\nGenerated comment:"

    custom_print(f"Sending request to AI model with prompt length: {len(prompt)} characters")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_APP_NAME,
            },
            data=json.dumps(
                {
                    "model": "google/gemma-2-9b-it:free",
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )
        response.raise_for_status()
        ai_comment = response.json()["choices"][0]["message"]["content"]
        custom_print("AI comment generated successfully")
        custom_print(f"Generated comment: {ai_comment}")
        return ai_comment
    except Exception as e:
        custom_print(f"Error generating AI comment: {str(e)}")
        return None

def post_comment(driver, ai_comment, post_url):
    custom_print("Attempting to post the AI-generated comment...")

    # Extract post ID from URL
    post_id = post_url.split("/")[-3]
    custom_print(f"Extracted postid: {post_id}")

    # Get CSRF token from cookie
    csrf_token = driver.get_cookie("csrf_token")["value"]

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
    
    return True

    # Make the POST request
  #  response = requests.post(
   #     f"https://www.reddiet.com/svc/shreddit/t3_{post_id}/create-comment",
   #     headers=headers,
   #     cookies=cookies,
   #     data=comment_data,
  #  )

  #  custom_print(f"Response status: {response.status_code}")
    # custom_print(f'Response headers: {response.headers}')

  #  if response.status_code == 200:
  #      return True
  #  else:
  #      return False


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
    persona,
    include_comments,
    ai_response_length  
):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    for header in custom_headers:
        chrome_options.add_argument(f"--{header}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        custom_print("WebDriver initialized successfully")
    except WebDriverException as e:
        custom_print(f"Error initializing WebDriver: {e}")
        return []

    all_collected_info = []  # To store results from all subreddits


    try:
        custom_print("Navigating to Reddit login page...")
        driver.get("https://www.reddit.com/login/")
        
        custom_print("Waiting for username field...")
        username_field = wait_for_element(driver, By.ID, "login-username")
        custom_print("Waiting for password field...")
        password_field = wait_for_element(driver, By.ID, "login-password")

        if username_field and password_field:
            custom_print("Entering username and password...")
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            custom_print("Logging in.. Waiting for articles to load...")
            
            try:
                WebDriverWait(driver, 240).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "shreddit-post"))
                )
                custom_print("Logged in. Articles loaded successfully")
            except TimeoutException:
                custom_print("Timeout waiting for login.")
                custom_print("Closing WebDriver...")
                driver.quit()

        for subreddit in subreddits:
            custom_print(f"\nStarting to scrape subreddit: r/{subreddit}")
            custom_print(f"Navigating to subreddit: r/{subreddit}, sort type: {sort_type}")
            subreddit_url = f"https://www.reddit.com/r/{subreddit}/{sort_type}/"
            driver.get(subreddit_url)
            custom_print("Waiting for page to load...")
            time.sleep(5)  # Wait for page to load

            custom_print("Scrolling to load more content...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            custom_print("Waiting for content to load after scrolling...")
            time.sleep(5)  # Wait for content to load after scrolling

            custom_print("Finding posts...")
            posts = driver.find_elements(By.TAG_NAME, "article")
            custom_print(f"Found {len(posts)} posts")

            collected_info = []
            for index, post in enumerate(posts[:max_articles], 1):
                try:
                    custom_print(f"Processing post {index}...")
                    title = post.get_attribute("aria-label")
                    shreddit_post = post.find_element(By.TAG_NAME, "shreddit-post")
                    url = "https://www.reddit.com" + shreddit_post.get_attribute("permalink")

                    custom_print(f"Post {index} - Title: {title}")
                    custom_print(f"Post {index} - URL: {url}")

                    comments = extract_comments(driver, url, max_comments)

                    

                    custom_print(f"Generating AI comment for post {index}...")
                    ai_comment = generate_ai_comment(title, comments, persona, include_comments, ai_response_length) 
                    
                    if ai_comment:
                        custom_print(f"Waiting random time before posting comment for post {index}...")
                        wait_time = random.uniform(min_wait_time, max_wait_time)
                        custom_print(f"Waiting for {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                        
                        custom_print(f"Posting AI-generated comment for post {index}...")
                        post_success = post_comment(driver, ai_comment, url)
                        if not post_success:
                            custom_print(f"Failed to post comment for post {index}")

                    collected_info.append({
                        "subreddit": subreddit,
                        "title": title,
                        "url": url,
                        "comments": comments,
                        "ai_comment": ai_comment,
                    })

                    
                except StaleElementReferenceException:
                    custom_print(f"Stale element reference for post {index}. Skipping...")
                except NoSuchElementException as e:
                    custom_print(f"Element not found for post {index}: {str(e)}. Skipping...")
                except Exception as e:
                    custom_print(f"An error occurred processing post {index}: {str(e)}. Skipping...")

            all_collected_info.extend(collected_info)
            custom_print(f"Scraping completed for r/{subreddit}. Total posts processed: {len(collected_info)}")

    except Exception as e:
        custom_print(f"An unexpected error occurred: {str(e)}")
    finally:
        custom_print("Closing WebDriver...")
        driver.quit()

    custom_print(f"Scraping completed for all subreddits. Total posts processed: {len(all_collected_info)}")
    return all_collected_info