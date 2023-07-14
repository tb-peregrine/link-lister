import sys
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag


def process_pages(urls, subdirectory, rss):
    # Create a dictionary to store the nested pages and their linked URLs
    nested_pages = {}

    for url in urls:
        nested_pages[url] = process_page(url, subdirectory, rss)

    return nested_pages


def process_page(url, subdirectory, rss):
    # Create a set to store the visited pages
    visited_pages = set()

    try:
        # Send a GET request to the page
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the links on the page
        links = soup.find_all('a')

        # Extract the linked URLs within the subdirectory, excluding the RSS feed URL
        linked_urls = set()
        for link in links:
            href = link.get('href')
            if href:
                absolute_url = urljoin(url, href)
                parsed_absolute_url = urlparse(absolute_url)
                if parsed_absolute_url.path.startswith(subdirectory) and absolute_url != rss and absolute_url != url:
                    cleaned_url = urldefrag(absolute_url)[0]  # Remove any anchors from the URL
                    linked_urls.add(cleaned_url)

        return linked_urls

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while processing {url}: {e}")
        return set()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <RSS.xml URL> <subdirectory> <limit>")
        sys.exit(1)

    rss_url = sys.argv[1]
    subdirectory = sys.argv[2]
    limit = int(sys.argv[3])

    try:
        # Send a GET request to the RSS feed
        response = requests.get(rss_url)
        response.raise_for_status()

        # Parse the XML content
        soup = BeautifulSoup(response.text, 'xml')

        # Find all the URLs in the RSS feed
        urls = [item.link.text for item in soup.find_all('item')[:limit]]  # Limit the number of URLs using the slicing operator

        nested_pages = process_pages(urls, subdirectory, rss_url)

        # Create a list of all unique URLs
        all_urls = set(urls)
        for linked_urls in nested_pages.values():
            all_urls.update(linked_urls)

        # Create the matrix
        matrix = []
        for row_url in all_urls:
            row = []
            for col_url in all_urls:
                if col_url in nested_pages.get(row_url, []):
                    row.append("X")
                else:
                    row.append("")
            matrix.append(row)

        # Write the matrix to a CSV file
        with open("matrix.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([""] + list(all_urls))  # Write column labels
            for row_url, row in zip(all_urls, matrix):
                writer.writerow([row_url] + row)

        print("Matrix saved as matrix.csv")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while processing the RSS feed: {e}")
