import click
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag


def process_pages(urls, subdirectory, rss, parent_class):
    # Create a dictionary to store the nested pages and their linked URLs
    nested_pages = {}

    for url in urls:
        nested_pages[url] = process_page(url, subdirectory, rss, parent_class)

    return nested_pages


def process_page(url, subdirectory, rss, parent_class):
    # Create a set to store the visited pages
    visited_pages = set()

    try:
        print(f'Processing {url}...', end=" ")
        # Send a GET request to the page
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the parent elements with the specified class
        parent_elements = soup.find_all(class_=parent_class)

        # Find all the links on the page
        links = soup.find_all('a')

        # Extract the linked URLs within the subdirectory, excluding the RSS feed URL
        linked_urls = set()
        for parent_element in parent_elements:
            links = parent_element.find_all('a')
            for link in links:
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    parsed_absolute_url = urlparse(absolute_url)
                    if parsed_absolute_url.path.startswith(subdirectory) and absolute_url != rss and absolute_url != url:
                        cleaned_url = urldefrag(absolute_url)[0]  # Remove any anchors from the URL
                        linked_urls.add(cleaned_url)

        print(f'Done! Found {len(linked_urls)} links.')
        return linked_urls

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while processing {url}: {e}")
        return set()


@click.command(help="Usage: python lister.py <RSS.xml URL> <subdirectory> [OPTIONS]")
@click.argument('rss_url')
@click.argument('subdirectory')
@click.option('-l', '--limit', type=int, default='-1', help="Analyze the first <limit> URLs in the RSS feed")
@click.option('-p', '--parent_class', default='blogpost-content', help="Search only for content nested underneath a parent element with <parent_class>")
def main(rss_url, subdirectory, limit, parent_class):
    try:
        if limit >= 0:
            print(f'Processing first {limit} pieces of content in {rss_url}...')
        else: print(f'Processing all content in {rss_url}...')

        # Send a GET request to the RSS feed
        response = requests.get(rss_url)
        response.raise_for_status()

        # Parse the XML content
        soup = BeautifulSoup(response.text, 'xml')

        # Find all the URLs in the RSS feed
        urls = [item.link.text for item in soup.find_all('item')[:limit]]  # Limit the number of URLs using the slicing operator

        nested_pages = process_pages(urls, subdirectory, rss_url, parent_class)

        # Create a list of all unique URLs
        all_urls = set(urls)
        for linked_urls in nested_pages.values():
            all_urls.update(linked_urls)

        # Create the matrix
        print("Building matrix...")
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

if __name__ == '__main__':
    main()