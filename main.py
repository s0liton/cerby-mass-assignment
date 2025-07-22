import os
import time
import requests
import csv
import argparse
from rich import print, pretty

subdomain = None
access_token = None
csv_file_path = 'accounts.csv'
accounts = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def assign_account_access(cerby_subdomain, cerby_access_token, cerby_account_id, cerby_principal_id, cerby_principal_type, cerby_principal_role):
    headers = {
        "Content-Type": "application/json",
        "Cerby-Workspace": cerby_subdomain,
        "Authorization": "Bearer " + cerby_access_token
    }
    # User and Team Ids need to be in a list.
    cerby_principal_id = [cerby_principal_id]

    # Take the Principal type and make it lower case to avoid case issues.
    cerby_principal_type = cerby_principal_type.lower()

    if cerby_principal_type == "team":
        assignment_type = "teamIds"
    else:
        assignment_type = "userIds"

    # Request Body.
    body = {
        "accountId": cerby_account_id, assignment_type: cerby_principal_id, "role": cerby_principal_role
    }

    response = requests.post(
        url="https://api.cerby.com/v1/accounts/share",
        headers=headers,
        json=body,
    )
    # If we're doing a dry run, don't actually make the request.
    if not args.dry_run:
        response.raise_for_status()

def write_results(account_list):
    # Write the results back to the original CSV file.
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(accounts)
        csv_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Cerby Mass Account Assignment tool helps you to bulk assign users or groups to Cerby-managed accounts with a given role.")
    parser.add_argument("--subdomain", required=True, help="Your Cerby Workspace's Subdomain e.g mycompany")
    parser.add_argument("--access_token", required=True, help="An access token for your user. You should have some level of permissions to these accounts or be a super administrator int he workspace.")
    parser.add_argument("--dry-run", action="store_true", required=False, default=False, help="Dry run, do not actually do anything." )
    args = parser.parse_args()

    clear_screen()
    print("|--------------------------------------|")
    print("|----- Cerby Mass Assignment Tool -----|")
    print("|--------------------------------------|")
    print("")
    with open(csv_file_path, mode='r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames

        # Load each row from the CSV into a temporary list.
        print("Found the following assignments in the CSV file:")
        for row in reader:
            accounts.append(row)

        # Close the file for now.
        csv_file.close()

    # Print up to 50 accounts and ask user for confirmation.
    pretty.pprint(accounts, max_length=50)
    print("Accounts to Process: " + str(len(accounts)))
    print("")
    confirm = input("Do you want to continue? [y/N] ")

    # If user confirms, begin processing.
    if confirm == ('y' or 'Y'):
        # Clear screen to keep things clean.
        print("Great! We'll start processing your assignments shortly...")
        time.sleep(2)
        clear_screen()

        # Add status row in existing CSV file to track progress, if it doesn't exist.
        if 'status' not in fieldnames:
            fieldnames.append('status')

        # Header for account view in terminal
        print("|---------------------------------|")
        print("|------ Account Assignments ------|")
        print("|---------------------------------|")
        print("")

        # Main account loop.
        for account in accounts:
            try:
                # Get this account's status.
                current_account_status = account.get('status', '').lower()

                # If the account does not show success in the status field, we should try it.
                if current_account_status != 'success':
                    # Make the assignment request to Cerby.
                    assign_account_access(args.subdomain, args.access_token, account["account_id"], account["principal_id"], account["principal_type"], account["role"])
                    # Mark the account as successfully processed if no error occurred.
                    account['status'] = 'success'
                    print(
                        f"Account ID: {account['account_id']} - Principal ID: {account['principal_id']} with role: [blue]{account['role']}[/blue] - Status: [green]{account['status']}[/green]")
                    # Mitigate rate limit problems by waiting 1 second between calls, should give us a theoretical max of < 60/min with processing time.
                    time.sleep(1)

            except requests.exceptions.HTTPError as error:
                # A failure happened, so mark the account as not_completed, so we can potentially try again on another run.
                account['status'] = 'not_completed'
                print(
                    f"Account ID: {account['account_id']} - Principal ID: {account['principal_id']} with role: [yellow]{account['role']}[/yellow] - Status: [red]{account['status']}[/red]")
                print("")
                status = error.response.status_code
                if status in (401, 403):
                    print(
                        f"Ending Run: Your token is invalid or lacking necessary permissions. Verify and run again. Status Code: {status}")
                    break
                if status in (400, 500):
                    print(f"A general error occurred: {error.response.text}, Status Code: {error.response.status_code}")
                    continue

        # If we get here, enough has happened to commit the statuses to the csv file. Only time we won't is if the
        # token was invalid. In that case, the very first account assignment will fail anyway.
        write_results(accounts)
        print("")
        print(f"Stats - Successful: {sum(1 for account in accounts if account['status'] == 'success')}, Error: {sum(1 for account in accounts if account['status'] != 'success')}")