import RedditFunctions as rf
import seaborn as sb
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

# A list of dictionaries defining the times and subreddits to analyze.

candidates = [
    {'subreddit': 'The_Donald', 'after': 1434412800, 'before': 1478563200},
    {'subreddit': 'SandersForPresident', 'after':1432598400 , 'before': 1469491200 },
    {'subreddit': 'hillaryclinton', 'after':1428796800 , 'before': 1478563200 },
    #{'subreddit': 'TedCruzForPresident', 'after':1427068800	 , 'before': 1462233600},
    #{'subreddit': 'TedCruz', 'after':1427068800, 'before': 1462233600},
    #{'subreddit': 'KasichForPresident', 'after': 1437436800, 'before': 1462320000},
    #{'subreddit': 'Marco_Rubio', 'after': 1428883200, 'before': 1458000000},
    {'subreddit': 'jillstein', 'after': 1434931200, 'before': 1478563200},
    {'subreddit': 'GaryJohnson', 'after': 1452038400, 'before': 1478563200}
    ]

def total_candidate_comments():
    '''
    Used to find the total number of comments candidates
    got on their reddits during their campaign

    Output: list of tuples
        [(subreddit,number of comments)]
             |              |
          string           int
    '''
    totals = []
    for c in candidates:
        comments = rf.total_comments(subreddit=c['subreddit'],before=c['before'],after=c['after'])
        totals.append((c['subreddit'],comments))
    
    return totals
        

def plot_total_candidate_comments():
    '''
    Displays a plot of all the candidates comments
    '''
    # Get data
    totals = total_candidate_comments()

    # Set up data
    t = [total[1] for total in totals]
    subreddits = [total[0] for total in totals]
    
    # Set up plot
    ax = sb.barplot(x=subreddits,y=t)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.title("Comments on Subreddit During Candidates' Campaigns")
    plt.ylabel("Number of Comments")
    plt.xlabel("Subreddit")
    plt.show()

def plot_candidate_comments_over_time():
    '''
    Displays a histogram of candidate's comments over time
    '''
    fig, ax = plt.subplots()

    artists = []

    for candidate in candidates:

        # Get histogram data for candidate
        aggs = rf.comments_over_time(subreddit=candidate['subreddit'],after=candidate['after'],before=candidate['before'])

        # The beginning date of each value
        binEdges = []

        # The value of each bin
        binValues = []

        # Format the values
        for agg in aggs:
            binValues.append(agg['doc_count'])
            binEdges.append(mdate.epoch2num(agg['key'])) # Change to num format for hist
        

        # Plot the date using plot_date rather than plot
        line = ax.plot_date(binEdges, binValues,ls='-',marker="None")

        artists.append(line)

    # Choose your xtick format string
    date_fmt = '%m-%d-%y %H:%M:%S'

    # Use a DateFormatter to set the data to the correct format.
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)

    # Sets the tick labels diagonal so they fit easier.
    fig.autofmt_xdate()

    # Label the graph
    plt.ylabel('Number of Comments Per Day')
    plt.xlabel('Date')
    plt.title('Comments over time')

    # Legend
    subreddits = [c['subreddit'] for c in candidates]
    plt.legend(subreddits,loc='upper left')

    plt.show()