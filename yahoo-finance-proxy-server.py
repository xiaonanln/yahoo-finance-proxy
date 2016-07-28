# coding: utf8

import tornado.ioloop
import tornado.web
import googlefinance
import json
import sys
import time
import requests
import pytz
import logging

from datetime import datetime

import symbolsdb


logging.getLogger().setLevel(logging.DEBUG)

EARLIEST_DATE = '1950-01-01' # 最早时间到1950年
TIMEZONE = pytz.timezone('US/Eastern')
logging.info('Timezone set to: %s', TIMEZONE)

SYMBOLS_DB_FILE = '_symbols.txt'

PORT = 28888

def getDate():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")

logging.info('Today: %s', getDate())

class MyRequestHandler(tornado.web.RequestHandler):
    def get_all_arguments(self):
        arguments = {}
        for key in self.request.arguments:
            arguments[key] = self.get_argument(key)
        return arguments

class MainHandler(MyRequestHandler):
    def get(self):
        self.write("Welcome to yahoo-finance-proxy")

class DownloadTableCsv(MyRequestHandler):

    def get(self):
        arguments = self.get_all_arguments()

        a = int(arguments['a'])
        b = int(arguments['b'])
        c = int(arguments['c'])
        d = int(arguments['d'])
        e = int(arguments['e'])
        f = int(arguments['f'])

        startDate = '%04d-%02d-%02d' % (c, a+1, b)
        stopDate = '%04d-%02d-%02d' % (f, d+1, e)
        logging.debug("DownloadTableCsv: startDate: %s, stopDate: %s", startDate, stopDate)

        symbol = arguments['s']

        data = symbolsdb.get(symbol, startDate, stopDate)
        if data is None:
            yahoo_finance_url = 'http://real-chart.finance.yahoo.com/table.csv?s={s}&d={d}&e={e}&f={f}&g={g}&a={a}&b={b}&c={c}&ignore={ignore}'.format(**arguments)
            logging.info("Loading %s ..." % yahoo_finance_url)

            resp = requests.get(yahoo_finance_url, timeout=10)
            if not resp.ok:
                self.send_error( resp.status_code )
                return

            data = resp.content
            symbolsdb.set(symbol, startDate, stopDate, data)
        else:
            logging.debug("Loaded %s from symbolsdb: %s ~ %s", symbol, startDate, stopDate)

        self.set_header("Content-Type", "text/html")
        self.write(data)

def make_app():
    return tornado.web.Application([
        (r"/table.csv", DownloadTableCsv),
        (r"/", MainHandler),
    ], compress_response=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    logging.info('Start listening on %s ...', PORT)
    tornado.ioloop.IOLoop.current().start()
