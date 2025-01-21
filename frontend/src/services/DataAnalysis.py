import requests

# Initialize variables
next_cursor = None
event_data = []

while True:
    try:
        # Make the API request
        response = requests.get(
            url="https://example.com/v1/events",  # Replace with your actual API URL
            params={
                "leagueID": "NBA",
                "startsAfter": "2024-04-01",
                "startsBefore": "2024-04-08",
                "finalized": True,
                "cursor": next_cursor
            }
        )
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Parse response JSON
        data = response.json()

        # Concatenate events
        event_data.extend(data.get("events", []))

        # Update cursor for pagination
        next_cursor = data.get("nextCursor")

        # Break loop if no next cursor
        if not next_cursor:
            break
    except requests.RequestException as error:
        print(f"Error fetching events: {error}")
        break

# Process the event data
for event in event_data:
    odds = event.get("odds", {})
    for odd_object in odds.values():
        odd_id = odd_object.get("oddID")
        score = float(odd_object.get("score", 0))  # Default to 0 if score is missing
        close_over_under = float(odd_object.get("closeOverUnder", 0))  # Default to 0 if missing

        # Determine the result
        if score > close_over_under:
            print(f"Odd ID: {odd_id} - Over Wins")
        elif score == close_over_under:
            print(f"Odd ID: {odd_id} - Push")
        else:
            print(f"Odd ID: {odd_id} - Under Wins")
