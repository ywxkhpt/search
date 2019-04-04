# -*- coding:utf-8 -*-
from search.facebook_search.run import run as facebook_run
from search.google_search.run import run as google_run
from search.linkedin_search.run import run as linkedin_run
from search.twitter_search.run import run as twitter_run


def test(name):
    facebook_run(name)
    google_run(name)
    linkedin_run(name)
    twitter_run(name)


if __name__ == "__main__":
    test("Rose")
