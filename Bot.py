import os
import praw
import random
import time
import datetime

from dotenv import load_dotenv



def CheckForKeyword(comment, sub):
    try:
        commentBody = comment.body.lower()
        
        # Check if the bot is blocked in this subreddit
        if(commentBody.find("i am a bot") != -1):
            # If it is, add this subreddit to the list of already searched and move on
            print("Adding subreddit to already searched")
            with open("SubredditsSearched.txt", 'a') as file:
                file.write(sub.id + '\n')
            return
            
            
        if(commentBody.find(" shrek ") != -1 or commentBody.find(" nemo ") != -1
           or commentBody.find(" bee ") != -1 or commentBody.find(" incredible ") != -1
           or commentBody.find(" car ") != -1 or commentBody.find(" cars ") != -1):
            # Check if this comment was already replied to by the bot
            alreadyReplied = False

            with open("AlreadyReplied.txt", 'r') as file:
                lines = file.readlines()

                for line in lines:
                    if(line.find(comment.id) != -1):
                        # Already replied to this one
                        alreadyReplied = True
                        print("Already replied to this comment")
                        break

            # If not replied, add it to the file and reply
            if not alreadyReplied: 
                with open("AlreadyReplied.txt", 'a') as file:
                    file.write(comment.id + '\n')

            # Get random quote from the said movie
            if(commentBody.find(" shrek ") != -1):
                movie = "Shrek"
                with open("Scripts/ShrekScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)

                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)

                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ':' or line[-2] == ']'):            # Particular treatement
                            continue
                        else:
                            if(line.find(':') != -1):
                                line = line[line.find(':') + 2 : ]
                            break

            elif(commentBody.find(" bee ") != -1):
                movie = "Bee Movie"
                with open("Scripts/BeeScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)

                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)

                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ':'
                           or line[-2] == ')' or line[-2] == '}'):            # Particular treatement
                            continue
                        else:
                            break

            elif(commentBody.find(" nemo ") != -1):
                movie = "Finding Nemo"
                with open("Scripts/NemoScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)

                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)

                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ']'
                           or line[-2] == ')'):            # Particular treatement
                            continue
                        else:
                            line = line[line.find(':') + 2 : ]
                            break

            elif(commentBody.find(" incredible ") != -1):
                movie = "The Incredibles"
                with open("Scripts/IncrediblesScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)

                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)

                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ']'):            # Particular treatement
                            continue
                        else:
                            line = line[line.find(':') + 2 : ]
                            break
            
            elif(commentBody.find(" car ") != -1 or commentBody.find(" cars ") != -1):
                movie = "Cars"
                with open("Scripts/CarsScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)

                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)

                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ']' or line.find(':') == -1):            # Particular treatement
                            continue
                        else:
                            line = line[line.find(':') + 2 : ]
                            break

            # Answer comment with line
            answer = f"Your random quote from the movie {movie} is:\t" + line
            print("Replying to\t", commentBody, "\nwith\t", answer)
            comment.reply(answer)
    except: # Ignore exceptions
        pass


def IterateComments(iterateThis, sub):
    # Each comment found can be an actual comment or a MoreComments
    for comment in iterateThis:
        # Check if it's not mine
        try:
            if(comment.author != "RandomMovieQuoteBot_"):
                CheckForKeyword(comment, sub)
                IterateComments(comment.refresh().replies, sub)
        except: # For some reason, iterateThis can still have MoreComments
            pass


def CheckPosts(subredditIterator):
    try:
        for sub in subredditIterator:
            # Check if it was searched recently
            alreadySearched = False
            with open("SubredditsSearched.txt", 'r') as file:
                lines = file.readlines()

                for line in lines:
                    if(line.find(sub.id) != -1):
                        alreadySearched = True
                        break

            if alreadySearched:
                continue

            # Add this sub to the list of already searched, so that it is not searched again in this cycle
            with open("SubredditsSearched.txt", 'a') as file:
                file.write(sub.id + '\n')

            print(f"\nChecking r/{sub}")

            print("Checking hot")
            for submission in sub.hot(limit = 10):    # Last 10 hot posts in each subreddit
                # Check if this thread had a problem in the past (or too old)
                problem = False
                with open("AlreadyReplied.txt", 'r') as file:
                    lines = file.readlines()

                    for line in lines:
                        if(line.find(submission.id) != -1):
                            # Yes, it had a problem
                            problem = True
                            break

                if problem:
                    continue

                # Add it to the blacklist it they're older than x time
                timeOfPost = datetime.datetime.fromtimestamp(submission.created)
                now = datetime.datetime.now()
                if((now - timeOfPost).total_seconds() > 60 * 60 * 24 * 7):    # If longer than a week, never check it again
                    with open("AlreadyReplied.txt", 'a') as file:
                        file.write(submission.id + '\n')

                print("Checking submission\t", submission.title)

                # submission.comments returns a CommentForest
                submission.comments.replace_more()
                IterateComments(submission.comments, sub)

            print("Checking new")
            for submission in sub.new(limit = 10):    # Last 10 new posts in each subreddit
                print("Checking submission\t", submission.title)

                # submission.comments returns a CommentForest
                submission.comments.replace_more()
                IterateComments(submission.comments, sub)

    except praw.exceptions.RedditAPIException:
        # This thread has some problem (locked, probably), so ignore it in the future
        with open("AlreadyReplied.txt", 'a') as file:
            file.write(submission.id + '\n')


# Get environment variables
load_dotenv(".env")
clientID = os.environ.get("CLIENT_ID")
secret = os.environ.get("SECRET")
userAgent = os.environ.get("USER_AGENT")
username = os.environ.get("REDDIT_USERNAME")
password = os.environ.get("PASSWORD")

# Log into Reddit
reddit = praw.Reddit(client_id = clientID, client_secret = secret,
                     user_agent = userAgent, username = username,
                     password = password)

print("Logged in")

# Main program loop
while True:
    # Search subreddits related to the movies that the program replies to
    CheckPosts(reddit.subreddits.search("shrek"))
    CheckPosts(reddit.subreddits.search("ogre"))
    CheckPosts(reddit.subreddits.search("bee"))
    CheckPosts(reddit.subreddits.search("movie"))
    CheckPosts(reddit.subreddits.search("film"))
    CheckPosts(reddit.subreddits.search("cinema"))
    CheckPosts(reddit.subreddits.search("nemo"))
    CheckPosts(reddit.subreddits.search("incredible"))
    CheckPosts(reddit.subreddits.search("fish"))
    CheckPosts(reddit.subreddits.search("animal"))
    CheckPosts(reddit.subreddits.search("car"))
    CheckPosts(reddit.subreddits.search("animation"))

    # Remove subreddits from SubredditsSearched.txt to start a new cycle
    with open("SubredditsSearched.txt", 'w') as file:
        pass

    # Wait and then check again
    time.sleep(60)   
    print("New cycle")






# Apprently you can't reply to posts in reddit with images
# So this bot will only answer with a random line from the script
# Anyway, this is the code for getting an image, for future me (possibly)
'''
# Got a hit, fetch images with user given query
response = sid.simple_image_download()

# Get the images (limit is 10 because the first ones might not have a known face in them)
response.download(keywords = comment.body, limit = 10)

# For some reason, we must ignore the first three images
# Before posting, try to open the image (some don't open for some reason)
iter = 4
found = False

while not found:
    print(f"Trying to open simple_images/{comment.body}/{comment.body}_{iter}.jpg")

    try:
        image = Image.open(f"simple_images/{comment.body}/{comment.body}_{iter}.jpg")
        found = True
        print("Image is suitable, answering comment")
    except:
        print("Image is not suitable, checking next")
        if(iter == 10):
            print("No suitable image found")
            skipComment = True
            break
        else:
            iter += 1

if skipComment:
    continue
'''
