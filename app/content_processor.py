# content_processor.py
import logging
from urllib.parse import urlparse
import concurrent.futures
from collections import defaultdict
from website_extractor import WebsiteExtractor
from config import MAX_WORKERS, CONTENT_SEPARATOR

def get_all_pages_content(urls, max_pages=100):
    """Get content from multiple pages in parallel with optimizations"""
    # Limit to max_pages
    urls = urls[:max_pages]
    
    if not urls:
        return ""
    
    logging.info(f"Processing {len(urls)} URLs")
    
    # Group URLs by domain to reuse extractors
    domains = defaultdict(list)
    for url in urls:
        domain = urlparse(url).netloc
        domains[domain].append(url)
    
    # Initialize extractors by domain (once per domain)
    extractors = {}
    for domain, domain_urls in domains.items():
        # Use a URL from the domain to initialize
        logging.info(f"Creating extractor for domain: {domain}")
        extractors[domain] = WebsiteExtractor(domain_urls[0])
    
    # Function to process a single URL
    def process_url(url):
        try:
            domain = urlparse(url).netloc
            extractor = extractors[domain]
            return extractor.get_page_content(url)
        except Exception as e:
            return ""
    
    # Process URLs in parallel using chunks to control load
    chunk_size = min(10, max_pages)  # Process in chunks of 10 or fewer
    results = []
    
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i+chunk_size]
        logging.info(f"Processing chunk {i//chunk_size + 1}/{(len(urls)-1)//chunk_size + 1} ({len(chunk)} URLs)")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {executor.submit(process_url, url): url for url in chunk}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:  # Only add successful results
                        results.append(result)
                except Exception as e:
                    logging.error(f"Error with {url}: {e}")
    
    # Combine with separator
    logging.info(f"Successfully processed {len(results)} pages")
    return CONTENT_SEPARATOR.join(results)