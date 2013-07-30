import sys
import MySQLdb as mdb
import dbinfo as DB

info = DB.getInfo()
db = None

try:
    
    # Open database connection
    db = mdb.connect( info["host"], info["username"],
        info["password"], info["dbName"] )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    
except mdb.Error, e:
    
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit(1)
    
finally:
    
    with open("./pdb_uniprot_chain_map.lst.2") as lines:
        for line in lines:
            att = line.split()
            
            sql = """SELECT m.PDBCode From modbase m WHERE m.PDBCode = """
            sql +=  """'""" + att[0] + """'"""
            
            cursor.execute(sql)
            result = cursor.fetchone()
            
            print "result: " + result 
            print "fasta: " + att[2]

    db.close()