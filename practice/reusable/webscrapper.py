import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def clean_and_convert_to_markdown(html_content):
    """
    Parses raw HTML, filters semantic text tags, and returns readable markdown.
    This saves valuable context tokens for ingestion into an AI model.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    output_lines = []
    
    # Target only core informational layouts sequentially 
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'tr']):
        text = element.get_text(separator=" ", strip=True)
        if not text:
            continue
            
        tag = element.name
        if tag == 'h1':
            output_lines.append(f"\n# {text}\n")
        elif tag == 'h2':
            output_lines.append(f"\n## {text}\n")
        elif tag == 'h3' or tag == 'h4':
            output_lines.append(f"\n### {text}\n")
        elif tag == 'li':
            output_lines.append(f"- {text}")
        else:
            output_lines.append(text)
            
    # Remove excessive blank margins and spacing
    content = "\n".join(output_lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()

def scrape_any_site_selenium(url, output_file="ai_input_data.txt"):
    print("🚀 Configuring headless browser environment...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Anti-bot detection mitigation strategy
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🌐 Fetching live target: {url}")
        driver.get(url)
        
        # Allow initial AJAX payloads and layout frameworks to spin up
        time.sleep(3) 
        
        # Trigger smooth bottom scrolling to safely unpack lazy-loaded blocks
        print("⏳ Parsing layout and triggering lazy-load content triggers...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        
        # Execute an optimized JS injector loop to drop junk components directly inside the browser DOM
        # This dramatically accelerates background memory processing
        print("✂️ Stripping boilerplate navigation elements, scripts, and footers...")
        driver.execute_script("""
            const junkElements = document.querySelectorAll('script, style, nav, footer, header, form, aside, iframe, noscript, svg, button');
            junkElements.forEach(el => el.remove());
        """)
        
        # Pull down the minimized cleanly isolated core HTML source tree
        raw_html = driver.page_source
        
        print("🧠 Transforming layout structures into clean text fields for the AI Model...")
        ai_ready_text = clean_and_convert_to_markdown(raw_html)

        return ai_ready_text
        # if ai_ready_text:
        #     with open(output_file, "w", encoding="utf-8") as f:
        #         f.write(ai_ready_text)
        #     print(f"✅ Success! Data compiled into '{output_file}' ({len(ai_ready_text)} characters)")
            
        #     print("\n--- Preview of AI-Ready Output Data ---")
        #     print("\n".join(ai_ready_text.split("\n")[:12]))
        # else:
        #     print("⚠️ Warning: Could not locate meaningful text clusters inside the target document structure.")
            
    except Exception as e:
        print(f"❌ Critical runtime engine exception handled: {e}")
        
    finally:
        print("🔒 Shutting down browser engine safely...")
        driver.quit()

