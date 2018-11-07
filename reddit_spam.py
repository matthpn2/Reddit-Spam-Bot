import praw
import time

common_spam = ["udemy", "course", "save", "coupon", "free", "discount"]

# setup credentials and create an authorized Reddit instance
reddit = praw.Reddit(client_id = "client_id",
                     client_secret = "client_secret",
                     user_agent = "user_agent",
                     username = "username",
                     password = "password")

def find_spam_by_name(search_query):
    '''
        Find and return a list of Reddit authors with submission posts matching the search query.
    '''
    authors = []
    for submission in reddit.subreddit("all").search(search_query, sort = "new", limit = 50):
        print(f"Title: {submission.title}\n Author: {submission.author}\n URL: {submission.url}\n")

        if submission.author not in authors:
            authors.append(submission.author)

    return authors

if __name__ == "__main__":
    while True:
        spam_content = []
        spam_users = {}

        suspicious_authors = find_spam_by_name("udemy")
        for author in suspicious_authors:
            spam_urls = []
            submission_count = 0
            spam_count = 0

            try:
                # iterate through new submissions to filter spam content
                for submission in reddit.redditor(str(author)).submissions.new():
                    sub_id = submission.id
                    sub_subreddit = submission.subreddit
                    sub_title = submission.title

                    dirty = False
                    # check if common spam words are contained within any submission title
                    for word in common_spam:
                        if word in sub_title.lower():
                            dirty = True

                            # check if url is already contained within list of spam urls
                            junk = [sub_id, sub_title, str(author)]
                            if junk not in spam_urls:
                                spam_urls.append(junk)
                    
                    # keep count of spam and submissions
                    if dirty:
                        spam_count += 1
                    submission_count += 1

                # add users to dictionary of spam users if 50% of their submissions are considered spam
                try:
                    spam_perc = spam_count / submission_count
                except:
                    spam_perc = 0.0
                print(f"User {str(author)} has a spam perc of {round(spam_perc, 3)}")

                if spam_perc >= 0.40 and submission_count > 1:
                    spam_users[str(author)] = [spam_perc, submission_count]

                    for spam in spam_urls:
                        spam_content.append(spam)
            
            except Exception as e:
                print(str(e))

        # post to the spam submissions
        for spam in spam_content:
            spam_id = spam[0]
            spam_user = spam[2]

            submission = reddit.submission(id = spam_id)
            created_at = submission.created_utc
            tagged_spam = False

            # check if already posted to the spam submission
            for comment in submission.comments.list():
                text = comment.body
                if "ᕕ( ᐛ )ᕗ uwu ᕕ( ᐛ )ᕗ" in text:
                    print("This submission has already been tagged spam.")
                    tagged_spam = True

            # if spam submission has not been tagged, proceed to tag
            if not tagged_spam and time.time() - created_at <= 432000:
                url = "https://reddit.com" + submission.permalink

                message = f"ᕕ( ᐛ )ᕗ uwu ᕕ( ᐛ )ᕗ\n\nI am a uwu bot that sniffs out spammers, and this smells like spam.\nAt least {round(spam_users[spam_user][0] * 100, 2)} out of the {spam_users[spam_user][1]} submissions from /u/{spam_user} appear to be for Udemy affiliate links.\nDon't let spam take over Reddit. Toss out this spammer.\n\nᕕ( ᐛ )ᕗ uwu ᕕ( ᐛ )ᕗ"
                try:
                    # check if already posted to the submission
                    with open("tagged_urls.txt", "r") as f:
                        tagged_submission = f.read().split('\n')
                    
                    # if submission has not been commented on, reply to it and write it to the tagged_urls text file
                    if url not in tagged_submission:
                        print(message)
                        submission.reply(message)
                        print(f"We've posted to {url} and now will sleep for 10 minutes.")

                        with open("tagged_urls.txt", "a") as f:
                            f.write(url + "\n")

                        time.sleep(10*60)
                        break
                except Exception as e:
                    print(str(e))
                    time.sleep(10*60)

# For more information, proceed to the PRAW documentation at https://praw.readthedocs.io/en/latest/index.html .