import sys
import time 
import MySQLdb as mdb
import dbinfo as DB

def hash(plate, mjd, fiberID):
	# this is a terrible hash function :)
    return plate+mdj+fiberID

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
	sys.exit(1)

finally:
	# Drop table if it already exist using execute() method.
	# ignore foreign keys when deleting
    
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    
    cursor.execute("DROP TABLE IF EXISTS lookup")
    #RUNTYPE CRC64   SequenceID  ModelID TargetBeg   TargetEnd   PDBCode PDBChain    PDBBegin
    #PDBEnd  SeqIdentity Evalue  ModelScore  ModPipeQualityScore ZDopeScore  ModelDate
    # add main table

    table = """CREATE TABLE lookup(
            PDB varchar(4) NOT NULL,
            CHAIN varchar(1) NOT NULL,
            FASTA varchar(6) NOT NULL,
            MODEL INT DEFAULT 0,
            PRIMARY KEY(FASTA, PDB, CHAIN) )
            """
            
    cursor.execute(table)    
# check foreign keys again
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    db.commit()
    
    idx = 0
    with open("./models_found.txt") as lines:
        
        for line in lines:
           
            att = line.split(',')
            
            sql = """SELECT COUNT(*) as c FROM (SELECT 1 FROM lookup l """
            sql += """WHERE l.FASTA = '"""
            sql += att[0]
            sql += """' ) as d """
            
            cursor.execute(sql)
            test = cursor.fetchone()
            
            if int(test[0]) > 0: # update table
                sql = """UPDATE lookup """
                sql += """SET MODEL = """ + att[1]
                sql += """ WHERE FASTA = '""" 
                sql += att[0] + """' """
                
                print sql
                
                cursor.execute(sql)
            else:
                sql = """INSERT INTO lookup (PDB, CHAIN, FASTA, MODEL) """
                sql += """VALUES ('NULL', '~', '""" 
                sql += att[0] + """', '""" + att[1] 
                sql += """')"""    
                
                print sql
                
                cursor.execute(sql)
                
            #initial table
            # att = line.split()
            # 
            # if len(att) < 3:
            #     att.append('NULL')
            # 
            # sql = """SELECT COUNT(*) as c FROM (SELECT 1 FROM lookup l """
            # sql += """WHERE l.PDB = '"""
            # sql += att[0] + """' and l.CHAIN = '""" 
            # sql += att[1] + """' and l.FASTA = '""" + att[2] + """' ) as d """
            # 
            # cursor.execute(sql)
            # test = cursor.fetchone()
            # 
            # if int(test[0]) > 0:
            #     #print test[0]
            #     continue    
            #     
            # #print values[-2]            
            # sql = """INSERT INTO lookup (PDB, CHAIN, FASTA, MODEL) """
            # sql += """VALUES ('""" 
            # sql += att[0] + """', '""" + att[1] + """', '""" + att[2] 
            # sql += """', 0)""" 
            #             
            # print sql
            # 
            # cursor.execute(sql)
            
db.commit()
# disconnect from server
db.close()
