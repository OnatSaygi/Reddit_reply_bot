import praw
import time
import sys
import threading
from requests.exceptions import ConnectionError

#globals
agent = ''
username = ''
password = ''
subreddit_name = 'all'
print_path, print_to_console, print_to_file = 'bot_log.txt', True, True
input_path = 'bot_input.txt'
sleep_time = 20 #seconds
comment_output_rate, submission_output_rate = 2000, 500


#classes and functions
class Save_log(object):
    def __init__(self, path, console, file):
        self.path=path
        self.console=console
        self.file=file
    def save(self, *string):
        string = time.asctime()[11:19]+" "+" ".join(map(str, string))+"\n"
        if self.console:
            sys.stdout.write(string)
        if self.file:
            f = open(self.path, 'a+')
            f.write(string)
            f.close()

def file_line_count(filename):
    lines = 0
    for line in open(filename): lines += 1
    return lines

class Text_parser(object): #searchs for keys in given string
    def __init__(self, path):
        self.path=path
        self.search = []
        self.reply = []
        self.input_file = open(path, 'r')
        for i in range(file_line_count(self.path)/2):
            self.add_list(self.input_file.readline()[:-1].replace('\\n', '\n'), self.input_file.readline()[:-1].replace('\\n', '\n'))
        self.input_file.close()

    def add_list(self, s, r):
        self.search.append(s)
        self.reply.append(r)

    def response(self, text):
        text=text.lower()
        for index in range(len(self.search)):
            if text.find(self.search[index])!=-1: return index
        return -1

def comment_finder(): #comment finder thread
    save_log.save("Starting comment finder")
    comment_count = 0
    for comment in praw.helpers.comment_stream(r, subreddit_name, verbosity=0):
        comment_count+=1
        if comment_count%comment_output_rate==0: save_log.save(comment_count, "comments have been processed")

        response_id = text.response(comment.body)
        if response_id!=-1 and str(comment.author)!=str(username):
            try:
                comment.reply(text.reply[response_id])
                save_log.save("Replied with index", response_id, "at", comment.link_id[3:]+"//"+comment.id, "to", str(comment.author))
            except praw.errors.APIException, err:
                save_log.save("Error, cannot reply with index", response_id, "at", comment.link_id[3:]+"//"+comment.id, "to", str(comment.author))

def submission_finder(): #submission finder thread
    #TODO check if replied before
    save_log.save("Starting submission finder")
    submission_count=0
    for submission in praw.helpers.submission_stream(r, subreddit_name, verbosity=0):
        submission_count+=1
        if submission_count%submission_output_rate==0: save_log.save(submission_count, "submissions have been processed")

        response_id = text.response(submission.title + submission.selftext)
        if response_id!=-1 and str(submission.author)!=str(username):
            try:
                submission.add_comment(text.reply[response_id])
                save_log.save("Replying with index", response_id, "at", "//"+submission.id, "to", str(submission.author))
            except praw.errors.APIException, err:
                save_log.save("Error, cannot repy with index", response_id, "at", "//"+submission.id, "to", str(submission.author))


save_log = Save_log(print_path, print_to_console, print_to_file)
text = Text_parser(input_path)
r = praw.Reddit(user_agent=agent)

#login
save_log.save('Boot')
while not r.is_logged_in():
    save_log.save("Trying to login as "+ username)
    try:
        r.login(username, password, disable_warning=True)
    except ConnectionError as err:
        save_log.save("Connection error")
        time.sleep(sleep_time)
save_log.save('Logged In')

#main loop
save_log.save("Running at /r/"+subreddit_name)
threading.Thread(target=comment_finder).start()
threading.Thread(target=submission_finder).start()
