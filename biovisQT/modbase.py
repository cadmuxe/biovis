import MySQLdb as mdb
import sys

try:
    
    con = mdb.connect('localhost', 'biovis', 'biovis', 'biovis');
    cur = con.cursor()