#accessing databse
import sqlite3

# plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import seaborn as sb

# Creating csv
import csv

#Getting JSON from webpage
#!/usr/bin/env python
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json



#Thank you Martin Thoma from stack overflow for this function
def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# Get Authors from database
def all_authors(sub,n):
    """
    Get's a list of everyone who ever posted more than n
    times on a subreddit who's database I have downloaded

    args:
        sub: string containing subreddit name
        n: min number of posts on the reddit to be included
    """

    # Get all the authors
    authors = sub_comments(sub,["author"])

    # Sum up total number of authors
    totalAuthors = {}

    for author in authors:
        if author[0] in totalAuthors:
            totalAuthors[author[0]]+=1
        else:
            totalAuthors[author[0]] = 1
    
    finalAuthors = []

    # Find all the authors that have more than n posts
    for key, value in totalAuthors.items():
        if value >= n:
            finalAuthors.append(key)
    
    return finalAuthors

def where_they_comment(author,after=None,before=None,size=500):
    """
    Used to figure out where author has been commenting

    Args:
        author = string of author name
        after = string of epoch time, will only look
                after this time
        before = string of epoch time, will only look
                 before this time
        size = int of how many posts you would like to agregate.
               will only work if 0 < n < 500
    
    Return:
        dictionary of format [{'doc_count' : times commented (int), 'key' : 'subreddit'}]
    """

    data = pushshift_comment(aggs='subreddit',fields='aggs',author=author,after=after,before=before,size=size)

    return data["aggs"]["subreddit"]

def where_subreddit_comments(sub,n,after=-1,before=-1):
    """
    Gets where an entire subreddit has been posting

    Args:
        sub    = string of sub to search
                 must be in local database
        n      = min number of comments to be considered a user
        after  = epoch value to search after
        before = epoch value to search before

    Returns:
        dict in form {subreddit : num posts}
    """
    authors = all_authors(sub,n)
    print("Retrieved authors")

    totalComments = {}

    for author in authors:
        authorComments = where_they_comment(author,after=after,before=before)
        for d in authorComments:
            if d['key'] in totalComments:
                totalComments[d['key']]+=d['doc_count']
            else:
                totalComments[d['key']] = d['doc_count']

    return totalComments


def top_dict_items(d,n):
    """
    Get the key,value pairs with the top n
    values from dict d

    Returns:
        list of tuples in accending order
    """

    listofTuples = sorted(d.items() ,  key=lambda x: x[1])

    return listofTuples[-n:]

def sub_comments(sub, fields):
    """
    Returns fields from sub[reddit] stored in local database

    input: 
        sub: string of subreddit name
        fields: list of strings

    output:
        list of lists
        return = (comment,comment,comment...)
        comment = (fields)

    Possible fields:
        idint: integer id
        idstr: string id
        created: epoch value of when created
        author: author name
        parent: str id of parent comment
        submission: str id of submission comment is found in
        body: body of text
        score: total score of upvotes and downvotes 
        subreddit: subreddit name 
        distinguish: idk
        textlen: length of text
    """
    # Define where database is in files
    location = '/Users/theobayarddevolo/AnacondaProjects/timesearch/subreddits/' + sub + "/" + sub + ".db"

    # Connect to db
    db = sqlite3.connect(location)

    #### Use cursor to get what we want ####
    cursor = db.cursor()

    # Set up command: '''SELECT field1 field2 ... FROM comments'''
    ex = '''SELECT '''
    for field in fields:
        ex = ex + field + ", "
    ex = ex[:-2] + ''' FROM comments'''
    print(ex)
    # Get data
    cursor.execute(ex)
    comments = cursor.fetchall()

    db.close() # IMPORTANT

    return comments

def rich_comment(comment):
    """
    determines whether a given comment is "rich"
    as in does it contain useful data?

    A rich comment has these qualities:
        - Between 50 and 750 characters
        - Does not start with a > as this indicates text being quoted

    These indicators were taken from the article 'Using Platform Signals for 
    Distinguishing Discourses: The Case of Men’s Rights and Men’s Liberation 
    on Reddit' by Jack LaViolette and Bernie Hogan
    """
    # TODO
    return None


def pushshift_comment(q = None, ids = None, size = None, fields = None, sort = None, 
    sort_type = None, aggs = None, author = None, subreddit = None, after = None, before = None, 
    frequency = None, metadata = None):
    """
    Returns a dictionary of the data returned from the pushift request 
    
    Input:
        q - Search term. (String)
        ids - Get specific comments via their ids (list of base36 ids)
        size - Number of search terms to return (0 < int < 501)
        fields - Which fields to return (list of strings)
        sort - Sort results in a specific order ("asc", "desc")
        sort_type - Sort by a specific attribute ("score", "num_comments", "created_utc")
        aggs - Return aggregation summary ("author", "link_id", "created_utc", "subreddit")
        author - Limit to specific author (string)
        subreddit - Limit to specific subreddit (string)
        after - Search after this time (int of epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days))
        before - Search before this time (int of epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days))
        frequency - Used with the aggs parameter when set to created_utc ("second", "minute", "hour", "day")
        metadata - display metadata about the query (bool)

    Output:
        dict - a dictionary of comments/info
    
    Thank you to Jason Baumgartner who hosts and maintains pushshift
    https://github.com/pushshift/api
    """
    # Make one giant dictonary for east formatting
    args = {"q":q,"ids":ids,"size":size,"fields":fields,"sort":sort,"sort_type":sort_type,"aggs":aggs,"author":author,"subreddit":subreddit,"after":after,"before":before,"frequency":frequency,"metadata":metadata}
    
    # Get rid of unused fields
    args = {key:value for key,value in args.items() if value is not None}

    # Prep list for url reqest
    for key, value in args.items():
        # Format lists as csv
        if value is list:
            temp = ""
            for el in value:
                temp = temp + el + ","
            args[key] = temp[:-1] # [:-1] to get rid of last comma
        
        # Make everything into strings
        if value is not str:
            args[key] = str(value)

    # Create url for request   
    url = "https://api.pushshift.io/reddit/search/comment/?"
    for key, value in args.items():
        url += key + "=" + value + "&"
    url = url[:-1] # Get rid of last &

    # Use url to get dictionary of info
    return get_jsonparsed_data(url)


def comments_over_time(subreddit = None, author = None, after = None, before = None, frequency = "day"):
    """
    Returns the total number of comments in [frequency] intervals between [after] and [before]

    Input:
        subreddit - restict to a subreddit (string)
        author - restrict to an account (string)
        after - return results after this date (int epoch value)
        before - return results before this date (int epoch value)
        frequency - bin size for comment count ("second", "minute", "hour", "day")
    Return:
        a list of dictionaries
        [{'doc_count':int,'key':int epoch value}]
           num comments    beginning of bucket
    """

    search = pushshift_comment(aggs="created_utc",subreddit=subreddit,author=author,after=after,before=before,frequency=frequency)
    return search["aggs"]["created_utc"]

def histogram_comments_over_time(reduction_factor=1,subreddit = None, author = None, after = None, before = None, frequency = "day"):
    """
    Displays a histrogram of the number of posts on a subreddit over time

    Input:
        reduction_factor - Used to multiply bin size (int)
        subreddit - restict to a subreddit (string)
        author - restrict to an account (string)
        after - return results after this date (int epoch value)
        before - return results before this date (int epoch value)
        frequency - bin size for comment count ("second", "minute", "hour", "day")
    Return:
        None
    """
    aggs = comments_over_time(subreddit=subreddit,author=author,after=after,before=before,frequency=frequency)


    # The beginning date of each value
    binEdges = []

    # The value of each bin
    binValues = []

    # Format the values
    for agg in aggs:
        binValues.append(agg['doc_count'])
        binEdges.append(mdate.epoch2num(agg['key'])) # Change to num format for hist
    
    # Decrease number of bins by REDUCTION_FACTOR
    reducedBinValues = []
    reducedBinEdges = []
    for i in range(len(binValues)):
        j = int(i/reduction_factor) # New index
        if i%reduction_factor == 0: # If its the begining of a new bin
            reducedBinEdges.append(binEdges[i])
            reducedBinValues.append(binValues[i])
        else:
            reducedBinValues[j]+=binValues[i]

    fig, ax = plt.subplots()

    # Plot the date using plot_date rather than plot
    ax.plot_date(reducedBinEdges, reducedBinValues,ls='-',marker="None")

    # Choose your xtick format string
    date_fmt = '%m-%d-%y %H:%M:%S'

    # Use a DateFormatter to set the data to the correct format.
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)

    # Sets the tick labels diagonal so they fit easier.
    fig.autofmt_xdate()

    # Make the graph look good
    plt.ylabel('Number of Comments')
    plt.xlabel('Date')
    if subreddit is not None:
        plt.title('Comments over time for {}'.format(subreddit))
    elif author is not None:
        plt.title('Comments over time for {}'.format(author))
    else:
        plt.title('Comments over time')

    plt.show()

def total_comments(subreddit = None, author = None, after = None, before = None):
    """
    A function to find the total number of comments made

    Input:
        subreddit - restict to a subreddit (string)
        author - restrict to an account (string)
        after - return results after this date (int epoch value)
        before - return results before this date (int epoch value)
    
    Output: 
        an int of the total number of comments
    """
    # Get aggregate result from pushshift
    comment_bins = comments_over_time(subreddit=subreddit,author=author,after=after,before=before)

    # Sum aggregate result
    total = 0
    for b in comment_bins:
        total += b['doc_count']
    
    return total

def save_all_comment_ids(subreddit,before=None,after=None):
    """
    Save a csv of all comment ids at comment_ids/[subreddit].csv

    Input:
        subreddit: string
        before: int, epoch value
        after: int, epoch value

    Output:
        none
    """

    csvFileLocation = "comment_ids/" + subreddit + ".csv"

    with open(csvFileLocation, mode = 'w') as csvFile:

        idWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)


    #TODO: Finish this function


