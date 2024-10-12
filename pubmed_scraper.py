import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("Script starting...")

# Define a desktop user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_pdf_link(pmc_url):
    try:
        pmc_response = requests.get(pmc_url, headers=headers)
        pmc_soup = BeautifulSoup(pmc_response.text, 'html.parser')
        
        selectors = [
            'li.pdf-link.other_item a',
            '.pmc-sidebar__formats li.pdf-link a',
            'a[href$=".pdf"]',
            '.format-menu a[href$=".pdf"]'
        ]
        
        for selector in selectors:
            pdf_elements = pmc_soup.select(selector)
            if pdf_elements:
                for pdf_element in pdf_elements:
                    if 'href' in pdf_element.attrs:
                        pdf_link = "https://www.ncbi.nlm.nih.gov" + pdf_element['href']
                        print(f"Found PDF link: {pdf_link}")
                        return pdf_link
        
        print(f"No PDF link found on {pmc_url}")
        return ""
    except Exception as e:
        print(f"Error accessing PMC page {pmc_url}: {str(e)}")
        return ""

def check_scihub(doi):
    scihub_url = f"https://sci-hub.wf/{doi}"
    try:
        response = requests.get(scihub_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for the "article not found" message
        not_found_message = soup.find('p', string="Unfortunately, Sci-Hub doesn't have the requested document:")
        if not_found_message:
            return "N/A"
        
        # Look for the iframe with id="pdf"
        iframe = soup.find('iframe', id='pdf')
        if iframe and 'src' in iframe.attrs:
            pdf_link = iframe['src']
            # If the link starts with '//', add 'https:' to the beginning
            if pdf_link.startswith('//'):
                pdf_link = 'https:' + pdf_link
            
            # Remove everything after .pdf
            pdf_link = pdf_link.split('.pdf')[0] + '.pdf'
            
            return pdf_link
        
        # If we can't find the iframe or the src attribute, return unable to find
        return "N/A"
    
    except Exception as e:
        print(f"Error accessing Sci-Hub for DOI {doi}: {str(e)}")
        return "Error accessing Sci-Hub"

def export_to_json(articles):
    with open('pubmed.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    
def scrape_pubmed():
    # Set up Selenium WebDriver (you need to have chromedriver installed and in your PATH)
    driver = webdriver.Chrome()
    
    # Navigate to the advanced search page
    driver.get("https://pubmed.ncbi.nlm.nih.gov/advanced/")
    
    # Input the query string
    query_string = '(("parent"[Title/Abstract] OR "mother"[Title/Abstract] OR "father"[Title/Abstract] OR "caregiver") AND ("emotion regulation"[Title/Abstract] OR "emotional regulation"[Title/Abstract] OR "affect regulation"[Title/Abstract] OR "coping strategies"[Title/Abstract] OR "stress management"[Title/Abstract]) AND (stress*[Title/Abstract] OR distress*[Title/Abstract] OR depress*[Title/Abstract] OR anx*[Title/Abstract] OR "fear"[Title/Abstract] OR "panic"[Title/Abstract] OR "MDD"[Title/Abstract] OR dysth*[Title/Abstract] OR "mood disorder"[Title/Abstract] OR "affective disorder"[Title/Abstract] OR "GAD"[Title/Abstract] OR "STAI"[Title/Abstract] OR "post*traumatic stress disorder"[Title/Abstract] OR "PTSD"[Title/Abstract] OR "social phobia"[Title/Abstract] OR "social anxiety"[Title/Abstract] OR "agoraphobia"[Title/Abstract] OR phob*[Title/Abstract] OR "obsessive-compulsive disorder"[Title/Abstract] OR "OCD"[Title/Abstract]) AND (ADHD[Title/Abstract] OR "attention deficit hyperactivity disorder")) OR (("parent"[Title/Abstract] OR "mother"[Title/Abstract] OR "father"[Title/Abstract] OR "caregiver"[Title/Abstract]) AND (stress*[Title/Abstract] OR distress*[Title/Abstract] OR depress*[Title/Abstract] OR anx*[Title/Abstract] OR "fear"[Title/Abstract] OR "panic"[Title/Abstract] OR "MDD"[Title/Abstract] OR dysth*[Title/Abstract] OR "mood disorder"[Title/Abstract] OR "affective disorder"[Title/Abstract] OR "GAD"[Title/Abstract] OR "STAI"[Title/Abstract] OR "post*traumatic stress disorder"[Title/Abstract] OR "PTSD"[Title/Abstract] OR "social phobia"[Title/Abstract] OR "social anxiety"[Title/Abstract] OR "agoraphobia"[Title/Abstract] OR phob*[Title/Abstract] OR "obsessive-compulsive disorder"[Title/Abstract] OR "OCD") AND ("parenting"[Title/Abstract] OR "mothering"[Title/Abstract] OR "fathering"[Title/Abstract] OR "mother-child"[Title/Abstract] OR "father-child"[Title/Abstract] OR "caregiver-child"[Title/Abstract] OR "style"[Title/Abstract] OR "practice"[Title/Abstract] OR "rearing"[Title/Abstract] OR "skill"[Title/Abstract] OR "warmth"[Title/Abstract] OR support*[Title/Abstract] OR responsiv*[Title/Abstract] OR "involvement"[Title/Abstract] OR affect*[Title/Abstract] OR control*[Title/Abstract] OR harsh*[Title/Abstract] OR monitor*[Title/Abstract] OR disciplin*[Title/Abstract] OR intrusive*[Title/Abstract] OR structur*[Title/Abstract] OR communicat*)AND (ADHD[Title/Abstract] OR "attention deficit hyperactivity disorder")) OR (("parent"[Title/Abstract] OR "mother"[Title/Abstract] OR "father"[Title/Abstract] OR "caregiver") AND ("emotion regulation"[Title/Abstract] OR "emotional regulation"[Title/Abstract] OR "affect regulation"[Title/Abstract] OR "coping strategies"[Title/Abstract] OR "stress management") AND ("parenting"[Title/Abstract] OR "mothering"[Title/Abstract] OR "fathering"[Title/Abstract] OR "mother-child"[Title/Abstract] OR "father-child"[Title/Abstract] OR "caregiver-child"[Title/Abstract] OR "style"[Title/Abstract] OR "practice"[Title/Abstract] OR "rearing"[Title/Abstract] OR "skill"[Title/Abstract] OR "warmth"[Title/Abstract] OR support*[Title/Abstract] OR responsiv*[Title/Abstract] OR "involvement"[Title/Abstract] OR affect*[Title/Abstract] OR control*[Title/Abstract] OR harsh*[Title/Abstract] OR monitor*[Title/Abstract] OR disciplin*[Title/Abstract] OR intrusive*[Title/Abstract] OR structur*[Title/Abstract] OR communicat*[Title/Abstract]) AND (ADHD[Title/Abstract] OR "attention deficit hyperactivity disorder"[Title/Abstract]))'
    
    query_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "query-box-input"))
    )
    query_box.send_keys(query_string)
    
    # Click the search button
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn"))
    )
    search_button.click()
    
    # Wait for the results to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".docsum-content"))
    )
    
    articles = []
    page_num = 1
    article_id = 1
    
    while True:
        print(f"Processing page {page_num}")
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        article_elements = soup.select('.docsum-content')
        print(f"Found {len(article_elements)} articles on this page")
        
        # Create a progress bar for the articles on this page
        for article in tqdm(article_elements, desc=f"Page {page_num}", unit="article"):
            title_element = article.select_one('.docsum-title')
            title = title_element.text.strip() if title_element else "No title found"
            
            link = title_element['href'] if title_element else None
            if not link:
                print(f"No link found for article: {title}")
                continue
            
            is_free = bool(article.select_one('.free-resources'))
            access_type = "FREE" if is_free else "PAID"
            
            article_url = f"https://pubmed.ncbi.nlm.nih.gov{link}"
            article_response = requests.get(article_url, headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            doi_element = article_soup.select_one('.id-link[data-ga-action="DOI"]')
            doi = doi_element.text.strip() if doi_element else "No DOI found"
            
            pdf_link = ""
            if is_free:
                pmc_link = article_soup.select_one('a.link-item.pmc')
                if pmc_link and 'href' in pmc_link.attrs:
                    pmc_url = pmc_link['href']
                    pdf_link = get_pdf_link(pmc_url)
                else:
                    print(f"No PMC link found for free article: {title}")
            
            # Check Sci-Hub if no PDF link is found
            if not pdf_link and doi != "No DOI found":
                scihub_link = check_scihub(doi)
                if scihub_link:
                    pdf_link = scihub_link
            
            article_data = {
                "id": article_id,
                "title": title,
                "doi": doi,
                "access_type": access_type,
                "pdf_link": pdf_link or "N/A"
            }
            articles.append(article_data)
            print(f"Found article: {title} | DOI: {doi} | {access_type} | PDF: {pdf_link or 'N/A'}")
            
            # Export to JSON after each article is processed
            export_to_json(articles)
            article_id += 1
        
        # Check if there's a next page
        next_button = driver.find_elements(By.CSS_SELECTOR, 'button.next-page-btn')
        if not next_button:
            print("No more pages to process")
            break
        
        # Click the next page button
        next_button[0].click()
        
        # Wait for the new page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".docsum-content"))
        )
        
        page_num += 1
    
    # Close the browser
    driver.quit()
    
    # Save articles to a CSV file
    with open('pubmed_articles.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'DOI', 'Access Type', 'PDF or SCI Hub Link'])
        for article in articles:
            writer.writerow([article['id'], article['title'], article['doi'], article['access_type'], article['pdf_link']])
    print(f"Found article {article_id}: {title} | DOI: {doi} | {access_type} | PDF: {pdf_link or 'N/A'}")
print("Starting scraper...")
scrape_pubmed()
print("Script finished.")