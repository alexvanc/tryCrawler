#!/usr/bin/python
#coding=utf-8
import git_crawler

crawler=git_crawler.GitCrawler("docker","docker","issues","mysql","crawler")
crawler.startCrawler()