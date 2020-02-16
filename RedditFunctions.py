# Accessing databse
import sqlite3

# Working with data
import pandas as pd

# plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import seaborn as sb

# Dealing with Files
import os
import glob
import shutil

#Getting JSON from webpage
#!/usr/bin/env python
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json



# Thank you Martin Thoma from stack overflow for this function
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
    as in does it contain useful data that is representative
    of the community?

    A rich comment has these qualities:
        - Between 50 and 750 characters
        - Does not start with a > as this indicates text being quoted
        - Has a score of at least 2

    These indicators were taken from the article 'Using Platform Signals for 
    Distinguishing Discourses: The Case of Men’s Rights and Men’s Liberation 
    on Reddit' by Jack LaViolette and Bernie Hogan as well as 'Cats and Captions vs. 
    Creators and the Clock: Comparing Multimodal Content to Context in Predicting 
    Relative Popularity' by Jack Hessel et al. 
    """
    # TODO finish this or delete it
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

def clean_csv(csvPath,after,before,minTextLength,maxTextLength):
    """
    This command will create a new csv file with only
    comments between the after and before times who's body character
    length is between minTextLength and maxTextLength. 
    
    The file is saved in the current directory

    Input:
        csvPath: String
        after: int (epoch value)
        before: int (epoch value)
        minTextLength: int
        maxTextLength: int 
    
    Output:
        None
    """

    comments = pd.read_csv(csvPath,low_memory=False)
    
    # minTextLength <= comment-length <= maxTextLength AND after < time-created < before
    filterExpressions = (comments.body.str.len()>=minTextLength, comments.body.str.len()<=maxTextLength, comments.created_utc > after, comments.created_utc < before)
    print(filterExpressions)

    comments = comments[all(filterExpressions)]

    comments.to_csv( "cleaned_csv.csv", index=False, encoding='utf-8-sig')

    #TODO fix this code

def csv_to_db(fileLocation, newFileName, tableName):
    """
    Converts a csv file to a db file

    Input:
        fileLocation: String of file path
        newFileName: String of db file name

    Output:
        None
    """

    db = sqlite3.connect(newFileName)

    csv = pd.read_csv(fileLocation)

    csv.to_sql(tableName,db)

    db.close()

def combine_csv_to_db(folderLocation, newFileName, tableName, maxNum=20):
    """
    Converts a multiple csv files to one db file

    Input:
        folderLocation: String of folder path
            - Folder must contain only csv files
        newFileName: String of db file name
        tableName: name of db table to add to
        maxNum: The maximum number of files to combine before stopping

    Output:
        None
    """
    originalDirectory = os.getcwd()
    processedFolder = "Finished"

    # Grab files names
    # Exclude already added items and database
    os.chdir(folderLocation)
    all_filenames = [i for i in glob.glob('[!{}]*[!*.db]'.format(processedFolder))]

    # Make sure there is a folder for processed files
    try:
        # Create target Directory
        os.mkdir(processedFolder)
        print("Directory " , processedFolder ,  " Created ") 
    except FileExistsError:
        print("Directory " , processedFolder ,  " already exists")

    db = sqlite3.connect(newFileName)

    # Add all the files to the db
    for fileName in all_filenames:
        # add to db
        csv = pd.read_csv(fileName, low_memory=False)
        csv.to_sql(tableName,db, if_exists="append")
        print(fileName, " added to database")

        # Move file to processed file
        shutil.move(fileName, processedFolder)

        # Check for maxNum
        maxNum += -1
        if (maxNum < 1):
            break

    # Clean up
    db.close()
    os.chdir(originalDirectory)

def prep_pairing_db(subDBs, totalComments, dbName, whatComments):
    """
    A function that creates a SQL database and populates it
    with the comments necessary for pairing.

    Input:
        - subDBs: a list of tuples with subreddit names and file paths
                [('subredditName', 'filePath'),...]
        - totalComments: the number of comments desired per subreddit after pairing
        - dbName: What to name the database
        - whatComments: str SQL paramaters for selection
                    ex: 'created_utc > 14200000 AND score > 1'
    
    Output:
        - Nothing is returned
        - An SQL database with a table for each subreddit
          with totalComments/number of subreddits "rich" comments
          in each table is created in the current directory
    """
    numComments = totalComments/len(subDBs)

    # Create db
    db = sqlite3.connect(dbName)

    for sub, dbLocation in subDBs:
        # Grab comments
        comments = get_rand_comments(dbLocation, 'Comments', numComments, whatComments)

        # add to db
        comments.to_sql(sub,db)

        print("Finished prepping",sub)


    # clean up
    db.close()

def get_rand_comments(dbLocation, dbTable, numItems, whatItems):
    """
    A command that returns a pandas dataframe of random items from
    a table in an SQL db

    Input:
        - dbLocation: str location of db file
        - dbTable: str table in the db to grab items from
        - numItems: int number of items to grab
        - whatItems: str SQL paramaters for what items to grab
                 ex: 'created_utc > 14200000 AND score > 1'
    
    Output:
        - returns a pandas dataframe of the items
    """
    db = sqlite3.connect(dbLocation)

    # Create request to get numItems random items from db
    dbRequest = "SELECT * FROM " + dbTable + " WHERE " + \
        whatItems + " ORDER BY RANDOM() LIMIT " + str(numItems)

    comments = pd.read_sql_query(dbRequest,db)

    db.close()

    return comments

def pair_comments(db, dbFrom, pairFromTable, toTable, whatItems, timeStamps):
    """
    Pairs comments closest in time to timeStamps from one db to another db

    Input:
        - db: sqlite3 connection to db to write comments to
        - dbFrom: sqlite3 connection to db to get comments from
        - pairFromTable: str name of table to take comments from
        - toTable: str name of table to add comments to
        - whatItems: str SQL paramaters for what items to grab
                 ex: 'created_utc > 14200000 AND score > 1'
        - timeStamps: a list of timeStamps to pair to
    
    Output:
        - None
    """
    # Add progress output so I don't go crazy waiting
    progress = 0
    numComments = len(timeStamps)

    # Set up dataframe [This approach is used to avoid having to know columns]
    comments = get_closest_comment(dbFrom, pairFromTable, timeStamps[0], whatItems)
    progress += 1
    print(progress, "comments paired out of:", numComments)


    for timeStamp in timeStamps[1:]:
        comment = get_closest_comment(dbFrom, pairFromTable, timeStamp, whatItems)
        comments = comments.append(comment)
        progress += 1
        print(progress, "comments paired out of:", numComments)
    

    comments.to_sql(toTable, db, if_exists='append')


def get_closest_comment(db, dbTable, timeStamp, whatItems):
    """
    Returns the closest comment in db to timeStamp as a pandas dataframe

    Input:
        - db: sqlite3 connection to db with attribute created_utc
        - dbTable: str name of table to grab from
        - timeStamp: int epoch value
        - whatItems: str SQL paramaters for what items to grab
                 ex: 'created_utc > 14200000 AND score > 1'
    
    Output:
        - a pandas dataframe
    """

    # Query that gets the closest comment to timeStamp that fits whatItems
    sqlQuery = "SELECT * FROM " + dbTable + " WHERE " + whatItems + \
        " ORDER BY abs(" + str(timeStamp) + " - created_utc) LIMIT 1"

    return pd.read_sql_query(sqlQuery,db)

def pair_prepped_comment_db(preppedDbLocation, subredditsDBs, whatItems):
    """
    Use after using prep_pairing_db to add paired comments

    Input:
        - preppedDbLocation: str the file location of prepped db
        - subredditsDBs: list of tuples [("subreddit name", "file location of db")] 
        - whatItems: str SQL paramaters for what items to grab
                 ex: 'created_utc > 14200000 AND score > 1'
    """
    db = sqlite3.connect(preppedDbLocation)
    subInfo = []

    # Get all time stamps before we staring adding comments
    for sub, dbLoc in subredditsDBs:
        sqlQuery =  "SELECT created_utc FROM " + sub
        timeStamps = [row[0] for row in db.execute(sqlQuery)]
        subInfo.append((sub,dbLoc,timeStamps))

    # # Pair each table
    # for sampleSub, _, timeStamps in subInfo:
    #     # for all subs that are not sample sub
    #     for targetSub, targetDbLoc, _ in [i for i in subInfo if i[0] != sampleSub]:
    #         pair_comments(db, targetDbLoc, "Comments", targetSub, whatItems, timeStamps)
    #         print("Paired", targetSub, "with",sampleSub)
    
    ## Pair each table
    # The most costly part of this is connecting to databases
    # So, this has all been coded to minimize that
    for targetSub, targetDbLoc, _ in subInfo:
        dbFrom = sqlite3.connect(targetDbLoc)
        print("Opened", targetSub, "db")
        # For every sub that isn't the target sub
        for sampleSub, _, timeStamps in [i for i in subInfo if i[0] != targetSub]:
            pair_comments(db, dbFrom, "Comments", targetSub, whatItems, timeStamps)
            print("Paired", targetSub, "with",sampleSub)
        
        dbFrom.close()

    # clean up
    db.close()