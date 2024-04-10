from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import UsernameOccupiedError, UsernameInvalidError
from telethon import functions
import time
import asyncio

async def print_info(client):
    # Print information about Telegram API workload
    try:
        dc_workload = await client(functions.help.GetNearestDcRequest())
        print(f"Telegram API workload: {dc_workload}")
    except Exception as e:
        print(f"Error retrieving Telegram API workload: {e}")

    # Print information about accepted username formats
    print("Accepted username formats: '@username' or '1. username'")

async def get_usernames():
    # Get usernames from the user
    usernames = []
    print("Please enter the usernames you want to check (press Enter after each username). Enter 'done' when finished:")
    while True:
        username = input().strip()
        if not username:
            continue
        if username.lower() == 'done':
            break
        if username[0].isdigit() and username[1] == '.':
            username = username.split('.', 1)[1].strip()  # Remove the number prefix
        usernames.append(username)
    return sorted(usernames)  # Sort the usernames alphabetically or numerically

async def check_usernames(usernames, client):
    taken_usernames = []
    free_usernames = []
    total_time = 0
    num_done = 0
    total_usernames = len(usernames)
    start_time = time.time()  # Track start time
    for username in usernames:
        try:
            start_username_time = time.time()  # Track start time for each username
            result = await client(functions.account.CheckUsernameRequest(username=username))
            free_usernames.append(username)
            print(f'Username {username} is available! Time elapsed: {time.time() - start_username_time:.5f} seconds')
        except UsernameOccupiedError:
            taken_usernames.append(username)
            print(f'Username {username} is taken. Time elapsed: {time.time() - start_username_time:.5f} seconds')
        except UsernameInvalidError as e:
            print(f'Username {username} is invalid: {e}. Time elapsed: {time.time() - start_username_time:.5f} seconds')
            taken_usernames.append(username)  # Add the username to taken_usernames list even if it's invalid
        except Exception as e:
            print(f'Error checking username {username}: {e}. Time elapsed: {time.time() - start_username_time:.5f} seconds')
            taken_usernames.append(username)  # Add the username to taken_usernames list in case of error
        num_done += 1
        print(f'{num_done}/{total_usernames} done. Total time: {time.time() - start_time:.5f} seconds', end='\r')  # Updating progress indicator
        time.sleep(0.1)  # Add a slight delay for smoother updating

    print()  # Move to the next line after the progress indicator
    return taken_usernames, free_usernames

async def main():
    api_id = input("Enter your API ID: ").strip()
    api_hash = input("Enter your API hash: ").strip()

    async with TelegramClient('session_name', api_id, api_hash) as client:
        await print_info(client)
        usernames = await get_usernames()
        if usernames:
            print("Checking usernames...")
            taken_usernames, free_usernames = await check_usernames(usernames, client)
            print("\nTaken usernames:")
            for username in taken_usernames:
                print(username)
            print("\nFree usernames:")
            for username in free_usernames:
                print(username)
            total_time = time.time() - start_time
            print(f"\nTotal time taken: {total_time:.5f} seconds")
            print(f"Total number of usernames checked: {len(usernames)}")
            print(f"Average time taken per username: {total_time/len(usernames):.7f} seconds")
        else:
            print("No usernames provided.")

        retry_check = input("Do you want to check more usernames? (yes/no): ").strip().lower()
        if retry_check == 'yes':
            await main()

if __name__ == "__main__":
    start_time = time.time()  # Start time for measuring total execution time
    asyncio.run(main())


