#!/usr/bin/env python3

import csv

PATH = "/home/owen/py/rt/rotten_tomatoes_movies.csv"
    # https://www.kaggle.com/stefanoleone992/rotten-tomatoes-movies-and-critics-datasets
    # last updated 2019/11/08
    # 16,638 rows 
    # temporary mirror: https://send.firefox.com/download/1dd68bdefb59f9e0/#vAsKiExvOYFg4zPTU6gK3w 


def parse(path):
    with open(path) as f:
        r = csv.DictReader(f)
        return list(map(Entry, r))

class Entry:

    def __init__(self, data):

        self.title = data['movie_title']
        self.link =  data['rotten_tomatoes_link']
        self.date = data.get('in_theaters_date') or data.get('on_streaming_date')

        # 'rating' field empty when 'count' field is 0
        self.rating_critic   = float(data['tomatometer_rating'] or 'NaN')
        self.rating_critic_n = int(data['tomatometer_count'] or 0)

        self.rating_aud   = float(data['audience_rating'] or 'NaN')
        self.rating_aud_n = int(data['audience_count'] or 0)

    def valid(self):
        # entries with no reviews will give the empty string
        return self.rating_critic.is_integer() and self.rating_aud.is_integer() \
                and self.rating_critic_n > 0 and self.rating_aud_n > 0

    def enough_ratings(self, min_ratings=50):
        return self.rating_critic_n >= min_ratings and self.rating_aud_n >= min_ratings

    def __str__(self):

        title = "{} ({})".format(self.title, self.date[:4])
        return "{:<45} Critic score {:>3} (n={:>3}), Audience score {:>3} (n={:>6})".format(
                title,
                int(self.rating_critic), self.rating_critic_n,
                int(self.rating_aud), self.rating_aud_n)

def biggest_difference(entries, critic_higher=False, num=100):
    def sort_key(entry):
        factor = 1 if critic_higher else -1
        return (entry.rating_aud - entry.rating_critic) * factor
    copy = list(entries)[:]
    copy.sort(key=sort_key)
    return copy

def fmt_group(header, entries):
    # format for github's markdown table viewer
    s = "\n"
    s += "## {}\n\n".format(header)
    s += "| Title | Critic score | Critic reviews | Audience score | Audience reviews |\n"
    s += "|-------|--------------|----------------|----------------|------------------|\n"
    for e in entries:
        title = "[{title} ({year})]({link})".format(title=e.title, year=e.date[:4],
                link="https://www.rottentomatoes.com"+e.link)
        s += "| {title} | {critic} | {critic_n} | {aud} | {aud_n} |\n".format(
                title=title,
                critic=int(e.rating_critic), critic_n = e.rating_critic_n,
                aud=int(e.rating_aud), aud_n=e.rating_aud_n)
    return s


if __name__=="__main__":
    SAMPLE = 30

    entries_all = parse(PATH)
    entries = list(filter(Entry.valid, entries_all))

    popularity_cutoff = 50  # omit reviews with too few ratings
    popularity_filter = lambda e: e.enough_ratings(min_ratings=popularity_cutoff)
    popular_entries = list(filter(popularity_filter, entries))

    print(fmt_group(
        "Popular (n≥{}) movies with higher audience scores".format(popularity_cutoff),
        biggest_difference(popular_entries)[:SAMPLE]))

    print(fmt_group(
        "Popular (n≥{}) movies with higher critic scores".format(popularity_cutoff),
        biggest_difference(popular_entries, critic_higher=True)[:SAMPLE]))

    print(fmt_group(
        "All movies with higher audience scores",
        biggest_difference(entries)[:SAMPLE]))

    print(fmt_group(
        "All movies with higher critic scores",
        biggest_difference(entries, critic_higher=True)[:SAMPLE]))


