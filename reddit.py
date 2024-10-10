import time
import requests
import json
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


def get_user_input(prompt, default, options=None):
    if options:
        print(f"{prompt} Options: {', '.join(options)}")
    user_input = input(f"{prompt} (default: {default}): ").strip().lower()
    if options and user_input and user_input not in options:
        print(f"Invalid option. Using default: {default}")
        return default
    return user_input if user_input else default


def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        print(f"Timeout waiting for element: {value}")
        return None


def truncate(text, max_length):
    return text if len(text) <= max_length else text[:max_length] + "..."


def extract_comments(driver, url, max_comments):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    print("Navigated to post page")

    comments = []
    try:
        # Wait for comments to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "shreddit-comment"))
        )

        # Find all comment elements
        comment_elements = driver.find_elements(By.CSS_SELECTOR, "shreddit-comment")

        for element in comment_elements[:max_comments]:
            try:
                # Extract comment text
                comment_text = element.find_element(By.CSS_SELECTOR, "div[slot='comment'] p").text.strip()
                
                # Extract author name
                author = element.get_attribute("author")
                
                # Extract comment depth and parent ID
                depth = int(element.get_attribute("depth"))
                parent_id = element.get_attribute("parentid")

                # Extract aria-label to determine if it's a top-level comment or reply
                aria_label = element.get_attribute("arialabel")

                if "thread level" in aria_label:
                    comment_info = f"Comment thread level {depth}: Reply from {author}"
                else:
                    comment_info = f"Comment from {author}"

                comments.append({
                    "text": comment_text,
                    "author": author,
                    "depth": depth,
                    "parent_id": parent_id,
                    "comment_info": comment_info
                })

                print(f"Extracted: {comment_info}")

            except NoSuchElementException:
                print("Skipping a comment due to missing elements")
            except Exception as e:
                print(f"Error extracting comment: {str(e)}")

    except TimeoutException:
        print("Timeout waiting for comments to load. Proceeding with available comments.")
    except Exception as e:
        print(f"An error occurred while extracting comments: {str(e)}")
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return comments

def generate_ai_comment(title, comments, persona):
    print("Generating AI comment... Please wait.")
    prompt = f"{PERSONAS[persona]} Based on the following article title generate an appropriate and insightful comment response to the article title, DO NOT INTERACT WITH THE OTHER EXISTING COMMENTS IN ANY WAY, ONLY RESPOND TO THE TITLE! Use the existing comments to determine an appropriate length for your answer, if they have short answers, so should you. :\n\nTitle: {title}\n\nExisting comments:\n"

    for comment in comments:
        indent = "  " * comment["depth"]
        prompt += f"{indent}{comment['comment_info']}:\n{indent}{comment['text']}\n\n"

    prompt += "\nGenerated comment:"

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
        print("AI comment generated successfully.")
        return ai_comment
    except Exception as e:
        print(f"Error generating AI comment: {str(e)}")
        return None
    
    
def post_comment(driver, ai_comment, post_url):
    print("Attempting to post the AI-generated comment...")

    # Extract post ID from URL
    post_id = post_url.split("/")[-3]
    print(f"Extracted postid: {post_id}")

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

    # Make the POST request
    response = requests.post(
        f"https://www.reddit.com/svc/shreddit/t4_{post_id}/create-comment",
        headers=headers,
        cookies=cookies,
        data=comment_data,
    )

    print(f"Response status: {response.status_code}")
    # print(f'Response headers: {response.headers}')

    if response.status_code == 200:
        return True
    else:
        return False


def login_and_scrape_reddit(
    username,
    password,
    subreddit,
    sort_type,
    max_articles,
    max_comments,
    pause_enabled,
    custom_headers,
    persona,
):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    for header in custom_headers:
        chrome_options.add_argument(f"--{header}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")
        return []

    collected_info = []

    try:
        # Navigate to Reddit login page
        driver.get("https://www.reddit.com/login/")
        print("Navigated to Reddit login page")

        # Input username and password
        username_field = wait_for_element(driver, By.ID, "login-username")
        password_field = wait_for_element(driver, By.ID, "login-password")

        if username_field and password_field:
            username_field.send_keys(username)
            password_field.send_keys(password)
            print(
                "Username and password entered. Please click the login button manually."
            )
            print("After logging in, the script will continue automatically.")

            # Wait for manual login and navigation to complete
            input("Press Enter after you've logged in and the page has loaded...")
        else:
            print("Could not find username or password field. Aborting.")
            return []

        # Navigate to the specified subreddit with the chosen sort type
        subreddit_url = f"https://www.reddit.com/r/{subreddit}/{sort_type}/"
        driver.get(subreddit_url)
        print(f"Navigated to {subreddit_url}")
        time.sleep(5)  # Wait for page to load

        # Scroll once to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for content to load after scrolling

        # Find all posts using the correct selector
        posts = driver.find_elements(By.TAG_NAME, "article")
        print(f"Found {len(posts)} posts")

        for index, post in enumerate(posts[:max_articles], 1):
            try:
                # Extract title from aria-label attribute
                title = post.get_attribute("aria-label")

                # Extract URL from permalink attribute
                shreddit_post = post.find_element(By.TAG_NAME, "shreddit-post")
                url = "https://www.reddit.com" + shreddit_post.get_attribute(
                    "permalink"
                )

                print(f"\nProcessing post {index}:")
                print(f"Title: {title}")
                print(f"URL: {url}")

                # Extract and display comments
                comments = extract_comments(
                    driver, url, max_comments
                )

                # Generate AI comment
                ai_comment = generate_ai_comment(title, comments, persona)

                if ai_comment:
                    print(f"AI-generated comment ({persona} persona): {ai_comment}")
                    post_success = post_comment(
                        driver, ai_comment, url
                    )  # Updated to include url
                    if not post_success:
                        print("Failed to post comment after multiple attempts.")

                collected_info.append(
                    {
                        "title": title,
                        "url": url,
                        "comments": comments,
                        "ai_comment": ai_comment,
                    }
                )

                if pause_enabled:
                    input("Press Enter to continue to the next post...")

            except StaleElementReferenceException:
                print(f"Stale element reference for post {index}. Skipping...")
            except NoSuchElementException as e:
                print(f"Element not found for post {index}: {str(e)}. Skipping...")
            except Exception as e:
                print(
                    f"An error occurred processing post {index}: {str(e)}. Skipping..."
                )

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        driver.quit()

    # Display summary of collected information
    print(f"\nTotal posts processed: {len(collected_info)}")

    return collected_info

def main():
    print("Welcome to the Reddit Scraper with Customizable AI-Generated Comments!")
    print("Press Enter to use default values for any prompt.")

    username = get_user_input("Enter your Reddit username", "bigbootyrob")
    password = get_user_input("Enter your Reddit password", "1893Apple")
    subreddit = get_user_input(
        "Enter the subreddit to scrape (without /r/)", "AskReddit"
    )
    sort_type = get_user_input("Enter the sort type", "hot", SORT_TYPES)
    max_articles = int(
        get_user_input("Enter the maximum number of articles to scrape", "10")
    )
    max_comments = int(
        get_user_input(
            "Enter the maximum number of comments to scrape per article", "10"
        )
    )
    pause_enabled = (
        get_user_input("Enable pausing between posts? (yes/no)", "no").lower() == "yes"
    )
    persona = get_user_input(
        "Choose AI response persona", "normal", list(PERSONAS.keys())
    )

    header_options = [
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "accept-language=en-US,en;q=0.9",
        "referer=https://www.google.com/",
    ]
    print("\nAvailable custom headers:")
    for i, header in enumerate(header_options, 1):
        print(f"{i}. {header}")
    header_choice = get_user_input(
        "Enter the numbers of headers to use (comma-separated, e.g., 1,2,3)",
        "1,2,3",
    )
    custom_headers = [
        header_options[int(i) - 1]
        for i in header_choice.split(",")
        if i.isdigit() and 1 <= int(i) <= len(header_options)
    ]

    collected_info = login_and_scrape_reddit(
        username,
        password,
        subreddit,
        sort_type,
        max_articles,
        max_comments,
        pause_enabled,
        custom_headers,
        persona,
    )

    # Display summary of collected information
    print("\nSummary of collected information:")
    for index, post in enumerate(collected_info, 1):
        print(f"\nPost {index}:")
        print(f"Title: {post['title']}")
        print(f"URL: {post['url']}")
        print(f"Number of comments scraped: {len(post['comments'])}")
        if post["ai_comment"]:
            print(f"AI-generated comment: {post['ai_comment']}")
        else:
            print("No AI-generated comment for this post.")

    print(f"\nTotal posts processed: {len(collected_info)}")

if __name__ == "__main__":
    main()