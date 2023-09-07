import click
from pprint import pprint
import re
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag


def search_keyword(urls, parent_class, keyword):
    print(f'Searching content for keyword "{keyword}"')
    
    # Create a dictionary to store URLs with the number of exact matches
    matching_urls = {}

    for url in urls:
        # Send a GET request to the page
        try:
            response = requests.get(url)
            response.raise_for_status()
        except:
            print(f"Could not access {url} due to a {response.status_code} error.")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the parent elements with the specified class
        parent_elements = soup.find_all(class_=parent_class)

        for parent_element in parent_elements:
            matches = parent_element.find_all(string=re.compile(keyword))
            # print(f'Found {len(matches)} matches of keyword "{keyword}" in {url}')
            if len(matches) > 0:
                matching_urls[url] = len(matches)

    return matching_urls


def process_pages(urls, subdirectory, rss, parent_class):
    # Create a dictionary to store the nested pages and their linked URLs
    nested_pages = {}

    for url in urls:
        nested_pages[url] = process_page(url, subdirectory, rss, parent_class)

    return nested_pages


def get_urls_from_rss(rss_url, match=None, limit=-1):
    try:
        if limit > 0:
            print(f'Processing first {limit} piece(s) of content in {rss_url}...')
        else: print(f'Processing all content in {rss_url}...')

        # Send a GET request to the RSS feed
        response = requests.get(rss_url)
        response.raise_for_status()

        # Parse the XML content
        soup = BeautifulSoup(response.text, 'xml')

        # Find all the URLs in the RSS feed that match (if passed)
        items = soup.find_all('item')

        # Create an empty array to store the URLs that match the conditions
        urls = []
        for item in items:     
            link = item.find('link').text.strip()
            title = item.find('title').text.strip()

            # Check if the match string is in the link or title
            if match:
                if match.lower() in link.lower() or match.lower() in title.lower():
                    urls.append(link)
                else:
                    pass
            else:
                urls.append(link)

        return urls[:limit]
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while processing the RSS feed: {e}")

def process_page(url, subdirectory, rss, parent_class):
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
@click.option('-m', '--match', help="Find only URLs that match.")
@click.option('-k', '--keyword', help="Search content from URLs in the RSS feed for a keyword and return a list of URLs containing the keyword exactly.")
@click.option('-e', '--just_list_em', is_flag=True, help="Just list all the blogs on the RSS feed, subject to the match and limit otpions")
def main(rss_url, subdirectory, limit, parent_class, match, keyword, just_list_em):
    urls = get_urls_from_rss(rss_url, match, limit)
    if just_list_em:
        try:
            slugs = [url.split('tinybird.co')[1] for url in urls]
        except:
            slugs = urls
        pprint(slugs)
        elements= '\n'.join(slugs)
        pyperclip.copy(elements)
        print("List copied to clipboard")
        return

    if keyword:
        matching_urls = search_keyword(urls, parent_class, keyword)
        pprint(matching_urls)
    else:    
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

if __name__ == '__main__':
    main()