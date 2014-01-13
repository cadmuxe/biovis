import sys
import time 
import MySQLdb as mdb
import dbinfo as DB

def hash(plate, mjd, fiberID):
	# this is a terrible hash function :)
    return plate+mdj+fiberID

info = DB.getInfo()

db = None
cursor = None

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
    
    cursor.execute("DROP TABLE IF EXISTS modbase")
	#RUNTYPE	CRC64	SequenceID	ModelID	TargetBeg	TargetEnd	PDBCode	PDBChain	PDBBegin
	#PDBEnd	SeqIdentity	Evalue	ModelScore	ModPipeQualityScore	ZDopeScore	ModelDate
	## add main table
	# "INSERT INTO table (name, id, datecolumn) VALUES (%s, %s, %s)",("name", 4,now)
	#import time    
    #time.strftime('%Y-%m-%d %H:%M:%S')

    table = """CREATE TABLE modbase(
            RUNTYPE varchar(16),
            CRC varchar(16),
            SequenceID varchar(40) NOT NULL,
            ModelID varchar(50),
            TargetBeg INT DEFAULT 0,
            TargetEnd INT DEFAULT 0,
            PDBCode varchar(4) NOT NULL,
            PDBChain varchar(2),
            PDBBegin INT DEFAULT 0,
            PDBEnd INT DEFAULT 0,
            SeqId FLOAT DEFAULT 0.0,
            Evalue FLOAT DEFAULT 0.0,
            ModelScore FLOAT DEFAULT 0.0,
            ModPipeQualityScore FLOAT DEFAULT 0.0,
            ZDopeScore FLOAT DEFAULT 0.0,
            ModelDate varchar(10) NOT NULL,
            FASTA varchar(6) NOT NULL,
		    PRIMARY KEY (SequenceID, PDBCode, ModelDate) )"""

    cursor.execute(table)    
	# check foreign keys again
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    db.commit()
    
    idx = 0
    with open("./modbase_models_pmp-20130725.txt") as lines:
        
        for line in lines:
            if idx == 0:
                idx += 1
                continue
            att = line.split()
            
            while len(att) < 16:
                att.insert(len(att)-2, '0.0')
                        
            values = ""
            
            if not att[8].isdigit() and not att[8][-1:].isdigit():
                print "eight: " + att[8]
                print "nine: " + att[9]
                
                att[8] = att[8][:-1]
                
            if not att[9].isdigit() and not att[9][-1:].isdigit():
                att[9] = att[9][:-1]
            
            for s in att:
                if s == 'NULL' or s == 'n/a':
                    s = '0.0'
                values += "'" + s + "'" + ", "
            
            sql = """SELECT COUNT(*) as c FROM (SELECT 1 FROM modbase m """
            sql += """WHERE m.SequenceID = '"""
            sql += att[2] + """' and m.PDBCode = '""" 
            sql += att[6] + """' and m.ModelDate = '""" + att[len(att)-1] + """' ) as d """
            
            cursor.execute(sql)
            test = cursor.fetchone()
                        
            if int(test[0]) > 0:
                #print test[0]
                continue    
                
            #print values[-2]            
            sql = """INSERT INTO modbase (RUNTYPE, CRC, SequenceID, ModelID, TargetBeg, """
            sql += """TargetEnd, PDBCode, PDBChain, PDBBegin, PDBEnd, SeqId, Evalue, ModelScore, """
            sql += """ModPipeQualityScore, ZDopeScore, ModelDate, FASTS) VALUES (""" 
            sql += values[:-2] 
            sql += """,'')""" 
            
            #print sql
            
            cursor.execute(sql)
            
db.commit()
# disconnect from server
db.close()
