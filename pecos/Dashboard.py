import pandas as pd
import numpy as np
import re
import logging
import os
import datetime
from glob import glob
from os.path import abspath, dirname, join
from string import Template
import pprint
import pecos

none_list = ['','none','None','NONE', None, [], {}]
nan_list = ['nan','NaN','NAN']

logger = logging.getLogger(__name__)
    
class Dashboard(object):

    def __init__(self):
        """
        Dashboard class
        """
        self.num_columns = 0
        self.num_rows = 0
            
    def write_HTML_dashboard(self, title, content, footnote='', logo=False):
        """
        Generate a Pecos report
        
        Parameters
        ----------
        title: string
        
        content : pd.DataFrame
        
        footnote : string (optional)
        
        logo : string (optional)
            Graphic to be added to the report header
        """
        
        logger.info("Writing HTML dashboard")
        
        # Set pandas display option     
        pd.set_option('display.max_colwidth', -1)
        pd.set_option('display.width', 40)
        
        html_string = _html_template(title, content, footnote, logo)
        
        # Write html file
        html_fname = join('Results', 'dashboard_' + title + ".html")
        html_file = open(html_fname,"w")
        html_file.write(html_string)
        html_file.close()
        
        logger.info("")
        
def _html_template(title, content, footnote, logo):
    
    template = """
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
    <title>"""
    template = template + title
    template = template + """
    </title>
    <meta charset="UTF-8" />
    </head>
    <table border="0" width="100%">
    <col style="width:70%">
    <col style="width:30%">
    <tr>
    <td align="left" valign="center">"""
    if logo:
        template = template + """
        <img  src=\"""" + logo + """\" alt='Logo' />"""

    template = template + """
    </td>
    <td align="right" valign="center">"""
    template = template + """ 
    </td>
    </tr>
    </table>
    <hr>
    <H2>
    Dashboard """
    template = template + title
    template = template + """
    </H2>
    <table border="1" class="dataframe">
    <thead>
    <tr>
    <th></th>"""
    for column in content.columns:
        template = template +  """
        <th align="center" valign="middle">""" + column + """</th>"""
    template = template + """
    </tr>
    </thead>
    <tbody>"""
    for row in content.index:
        template = template + """
        <tr>"""
        template = template +  """
        <th align="center" valign="middle">""" + row + """</th>"""
        for column in content.columns:
            template = template + """
            <td align="center" valign="middle">"""
            if content.loc[row, column]['href']:
                template = template + """<A href=\"""" + content.loc[row, column]['href'] + """\">"""
            for im in content.loc[row, column]['images']:
                template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"250"><br>"""
            if content.loc[row, column]['href']:
                template = template + """</A>"""
            template = template + """</td>"""
       
        template = template + """
        </tr>"""
   
    template = template + """
    </tbody>
    </table> 
    <br>"""
    template = template + footnote + """<br><br>"""
    template = template + """
    This report was generated by <A href="https://pypi.python.org/pypi/pecos">Pecos</A> """
    date = datetime.datetime.now()
    datestr = date.strftime('%m/%d/%Y')
    template = template + pecos.__version__ + ", " + datestr
    template = template + """
    </html>"""
    
    template = template + """
    </html>"""
    
    return template