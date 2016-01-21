#!/usr/bin/python
import flow_crawler

crawler=flow_crawler.FlowCrawler("docker","mysql","crawler")
crawler.startCrawler()
