# Broken Backlinks Similarity Search

## Installation

Before using this tool, make sure you have installed the necessary requirements.

## Setup

1. Create a new `.env` file and fill in the required parameters.

```bash
# Firefall Service
FIREFALL_API_KEY =
FIREFALL_IMSS_ORG = 

# IMSS Prod
IMSS_CLIENT_ID_PROD=
IMSS_CLIENT_SECRET_PROD=
IMSS_SERVICE_PERMANENT_AUTHORIZATION_CODE_PROD=

# IMSS Stage
IMSS_CLIENT_ID_STAGE = 
IMSS_CLIENT_SECRET_STAGE = 
IMSS_SERVICE_PERMANENT_AUTHORIZATION_CODE_STAGE = 
```

## Usage

To create broken backlink suggestions for a new website, follow these steps:

1. Open a new folder under the `data` directory and name it after the new website. 
2. Obtain the JSON files of broken backlinks and top 200 pages for the website using Ahref.
3. Move these JSON files into the respective website folder.
4. Scrape the content of the top 200 website pages using the scraper notebook:
   - Run the helper scripts.
   - Modify the website name and data path parameters.
   - Execute the scraper.
   - Check the scraped content located in the `data/name_of_the_website/scraped_content` folder.
   > Note: The scraper requires credentials to access the Firefall service. The current scraping model in use is gpt-4-turbo.
5. Duplicate the `similarity_petplace.ipynb` notebook and create a new one for the website.
6. Update the website name, path to the broken backlinks JSON, and webpage URL parameters in the new notebook.
7. Run all the scripts, calculate and save the embeddings using the FAISS library.
   > Note: This step needs to be executed only once. For subsequent similarity checks, skip this step.
8. Find the suggestions in the `data/name_of_the_website` folder. The filename will be `name_of_webpage_ai_suggestion_by_link.csv`.
   - In the CSV file, you will find the broken backlink and three suggestions from the scraped top 200 pages of the website.
   - The suggestions are based on the similarity of terms in the broken backlink and the text content of the pages.
   - You can compare the distance (where smaller distance indicates a closer match) information.
   - Consider the pageviews of the suggestion URLs during the decision-making process for the broken backlink.