# Nested Page Link Extractor

The Nested Page Link Extractor is a Python script that extracts links from nested pages within a specified subdirectory of a website. It takes a RSS feed URL as input, retrieves the URLs listed in the feed, and then processes each URL to find all the links within the specified subdirectory.

The script generates a matrix that represents the relationship between the processed URLs. The matrix is stored as a CSV file where each row and column corresponds to a URL, and an 'X' is placed in the matrix if a link exists between the URLs.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/tb-peregrine/link-lister.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python script.py <RSS.xml URL> <subdirectory> [OPTIONS]
```

### Arguments:
- `<RSS.xml URL>`: The URL of the RSS feed to retrieve the URLs from.
- `<subdirectory>`: The subdirectory of the website to search for links within.

### Options
- `-l`, `--limit`: The maximum number of URLs to process from the RSS feed. Processes the first `<limit>` links.
- `p`, `--parent_class`: The class name of the parent element within which you want to search for links.

Example:

```bash
python script.py https://example.com/rss.xml /blog -limit 10 -parent_class article-container
```

The script will retrieve the first 10 URLs from the specified RSS feed, process each URL to find the links within the "/blog" subdirectory, and generate a matrix of the link relationships.

## Output
The matrix will be saved as a CSV file named "matrix.csv" in the current directory.

## License & Copyright

Copyright 2023 by Cameron Archer

Licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

