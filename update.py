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
    count = 0
    with open("./pdb_uniprot_chain_map.lst.2") as lines:
        for line in lines:
            att = line.split()
            
            if len(att) < 3:
                continue
            
            sql = """SELECT m.PDBCode From modbase m WHERE m.PDBCode = """
            sql +=  """'""" + str(att[0]) + """'"""
            
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result is not None:
                count += 1
                sql = """UPDATE modbase SET FASTA="""
                sql += """'""" + str(att[1]) + """'"""
                sql += """WHERE PDBCode="""
                sql += """'""" + str(att[0]) + """'"""
                    
                cursor.execute(sql)
            
                print "result: " + str(result)
                print "fasta: " + str(att[2])
    print count
    db.commit()
    db.close()