import os
import praw
import random
import time
import datetime

from dotenv import load_dotenv



def CheckForKeyword(comment):
    try:
        commentBody = comment.body.lower()
        
        if(commentBody.find(" shrek ") != -1 or commentBody.find(" up ") != -1 or commentBody.find(" bee ") != -1):
            # Check if this comment was already replied to by the bot
            alreadyReplied = False
            
            with open("AlreadyReplied.txt", 'r') as file:
                lines = file.readlines()
                
                for line in lines:
                    if(line.find(comment.id) != -1):
                        # Already replied to this one 
                        alreadyReplied = True
                        break
                
            if alreadyReplied:
                print("Already replied to this comment")
                return
            else:   # If not replied, add it to the file and answer
                with open("AlreadyReplied.txt", 'a') as file:
                    file.write(comment.id + '\n')

            # Get random quote from the said movie
            if(commentBody.find(" shrek ") != -1):
                movie = "Shrek"
                with open("ShrekScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)
                    
                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)
                        
                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ':'):            # Particular tratement
                            continue
                        else:
                            break
            if(commentBody.find(" bee ") != -1):
                movie = "Bee Movie"
                with open("BeeScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)
                    
                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)
                        
                        line = lines[randomLine]
                        if(line == '\n' or line[-2] == ':'):            # Particular tratement
                            continue
                        else:
                            break
            if(commentBody.find(" up ") != -1):
                movie = "Up!"
                with open("UpScript.txt", 'r') as file:
                    lines = file.readlines()
                    numLines = len(lines)
                    
                    # Find a suitable line
                    while True:
                        randomLine = random.randint(0, numLines - 1)
                        
                        line = lines[randomLine].lstrip()    # Remove tralling and leading spaces
                        if(line == '\n' or line[-2] == ')'):            # Particular tratement
                            continue
                        else:
                            # This script has lines divided by '\n'. Check for this
                            check = 1
                            while(lines[randomLine + check] != '\n'):           # Check if next has text
                                line = line[:-1] + ' ' + lines[randomLine + check].lstrip()
                                check += 1
                
            # Answer comment with line
            answer = f"From the movie {movie}:\t" + line
            print("Replying to\t", commentBody, "\nwith\t", answer)
            comment.reply(answer)
    except: # Ignore exceptions
        pass
                    
        
def IterateComments(iterateThis):
    # Each comment found can be an actual comment or a MoreComments
    for comment in iterateThis:
        # Check if it's not mine
        if(comment.author != "RandomMovieQuoteBot_"):
            CheckForKeyword(comment)
            IterateComments(comment.refresh().replies)
        
                   
def CheckPosts(subredditIterator):
    try:
        for sub in subredditIterator:
            # Add this sub to the list of already searched, so that no one searches it again in this cycle
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
                IterateComments(submission.comments)
                
            print("Checking new")
            for submission in sub.new(limit = 10):    # Last 10 new posts in each subreddit
                print("Checking submission\t", submission.title)
                
                # submission.comments returns a CommentForest
                submission.comments.replace_more()
                IterateComments(submission.comments) 
                
    except praw.exceptions.RedditAPIException:
        # This thread has some problem (locked, probably), so ignore it in the future
        with open("AlreadyReplied.txt", 'a') as file:
            file.write(submission.id + '\n')
          
            
# Get environment variables
load_dotenv(".env")
clientID = os.environ.get("CLIENT_ID")
secret = os.environ.get("SECRET")
userAgent = os.environ.get("USER_AGENT")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Log into Reddit, we're going to reply to comments in several subreddits
reddit = praw.Reddit(client_id = clientID, client_secret = secret, user_agent = userAgent, username = username, password = password)

print("Logged in")

# Main program loop
while True:
    # Search subreddits related to the movies that we want to answer to
    CheckPosts(reddit.subreddits.search("shrek"))
    CheckPosts(reddit.subreddits.search("ogre"))
    CheckPosts(reddit.subreddits.search("bee"))
    CheckPosts(reddit.subreddits.search("up"))
    CheckPosts(reddit.subreddits.search("movie"))
        
    # Remove subreddits from the SubredditsSearched.txt to start a new cycle
    with open("SubredditsSearched.txt", 'w') as file:
        file.write('')
        
    time.sleep(60)   # Wait and then check again     
    print("Checking again") 
                    
                    
                    
                    
                    
                    
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