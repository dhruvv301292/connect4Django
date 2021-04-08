# s21_team_32
Repository for s21_team_32

## Usage
Within the virtual environment,

Make migrations
- python manage.py makemigrations connect4

Migrate
- python manage.py migrate connect4

Run the server
- python manage.py runserver


### Flow for Sprint #2

User Experience:
- Go to the PlayArea on the website
- See basic PlayArea page
- Click on Join game
- 2 Users click join to get added to a room (One after the other)
- Once 2 users have joined, First user sees a button to start the game - AJAX
- Bpth users are then redirected to the Game page as Players
- Players see initial empty board
- Players take turn to drop colored disks
- Game Progresses
- Any relevant messages are shown to handle edge cases
- Game Ends
- Winner (if any) is declared

Client
- Sends: gameid, player, column (request)
- Receives: board, message (response)

Views
- Handles Client requests
- Uses the Game API that facilitates the game
- GameObject stored as a model and is updated using relevant API methods
- Renders the updated game state to both players
