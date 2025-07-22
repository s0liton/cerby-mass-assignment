# Cerby Mass Assignment Tool

## Introduction
This tool allows you to handle bulk assignments of Cerby-managed accounts to users or teams(groups) through the Cerby API. This is useful when you want a quick way of assigning access to accounts without having to script it yourself.

## Requirements
- A Cerby Access Token from a user with sufficient permission to act on the accounts. [Instructions](https://help.cerby.com/en/articles/9450993-retrieve-a-bearer-token)
- Your Cerby subdomain (e.g `mycompany.cerby.com`, enter `mycompany`)
- A CSV file with a unique account assignment per row. You will need the following values:
  - Account ID
  - Principal ID (User or Team ID in Cerby)
  - Principal Type (`team` or `user`)
  - The role to assign (`collaborator`, `manager`, `owner`)
  - **Note**: Use the included `accounts.csv` as an example.
## Usage
- Navigate into the tool's root directory and create a virtual environment: `python -m venv venv`
- Activate your virtual environment:
  - Linux/macOS
    - `source venv/bin/activate`
  - Windows
    - `venv\Scripts\activate.bat`
- Install Required Libraries: `pip install -r requirements.txt`
- Modify the CSV file as you see fit.
- Run the tool
  - `python main.py --subdomain <your-subdomain> --access_token <your-access-token>`

## How It Works
The tool will parse your CSV file and attempt to perform each assignment against the Cerby API. It will iterate through all accounts in the file and attempt the assignment. The tool will then update your existing CSV file with a status for each account. This will ensure that you can track which assignments succeed or fail, and easily try them again
without duplicating requests.
