
import mysql.connector

class database():
    def __init__(self):
        self.isClosed = False
        self.cnx = mysql.connector.connect(user= "owl", password = "owl2020F", host ="autoattendence.cwmsb6usx5sg.us-west-2.rds.amazonaws.com", port = 3306, database = "FileOwl")
        self.cur = self.cnx.cursor()
    def close(self):
        if(not(self.isClosed)):
            try:
                self.cnx.commit()
                self.cnx.close()
                self.isClosed = True
            except:
                pass
    def addFire(self,lat,lon,dat,mesg,intensity,smoke):
        cur = self.cur
        cur.execute("INSERT INTO allFires (dateObserved,lat,lon,info,intensity,smoke,windSpeed) VALUES ('%s',%s,%s,'%s',%s,%s,0) " %(dat,lat,lon,mesg,intensity,smoke) )
        self.cnx.commit()

    def addFireGOV(self,lat,lon,dat,mesg,intensity,smoke,govID):
        cur = self.cur
        cur.execute("SELECT fireID FROM allFires WHERE govId = '%s'" % (govID))
        out = 0
        for c in cur:
            out = int(c[0])

        if(out == 0):
            cur.execute("INSERT INTO allFires (dateObserved,lat,lon,info,intensity,smoke,govId) VALUES ('%s',%s,%s,'%s',%s,%s,'%s') " %(dat,lat,lon,mesg,intensity,smoke,govID) )
            self.cnx.commit()
        else:
            cur.execute("UPDATE allFires SET intensity=%s WHERE fireID = %s" %(intensity,out) )
            self.cnx.commit()



    def getFires(self):
        cur = self.cur
        cur.execute("SELECT lat,lon,fireID FROM allFires")
        out = []
        for c in cur:
            out.append([float(c[0]),float(c[1]),int(c[2])])
        return out
    def getFiresWind(self):
        cur = self.cur
        cur.execute("SELECT lat,lon,fireID,windSpeed FROM allFires")
        out = []
        for c in cur:
            out.append([float(c[0]),float(c[1]),int(c[2]),int(c[3])] )
        return out

    def getFiresXY(self):
        cur = self.cur
        cur.execute("SELECT lat,lon FROM allFires")
        out = []
        for c in cur:
            out.append([float(c[0]),float(c[1])])
        return out
    def getFiresXYWeight(self, intens):
        cur = self.cur
        cur.execute("SELECT lat,lon FROM allFires WHERE intensity = %s" %(intens))
        out = []
        for c in cur:
            out.append([float(c[0]),float(c[1])])
        return out

    def getFire(self,fireID):
        cur = self.cur
        cur.execute("SELECT lat,lon,fireID,info,intensity,smoke FROM allFires WHERE fireID = %s" %(fireID))
        out = []
        for c in cur:
            out.append([float(c[0]),float(c[1]),int(c[2]),str(c[3]),int(c[4]),int(c[5])])
        return out



    def getFiresByDate(self,lat,lon,dateFrom,dateTo):
        cur = self.cur
        cur.execute("SELECT fireID,lat,lon FROM allFires WHERE dateObserved >= '%s' AND dateObserved <= '%s'" %(dateFrom,dateTo))
        out = []
        for c in cur:
            out.append([float(c[1]),float(c[2]),int(c[0])])
        return out

    def getAllFireInfo(self):
         cur = self.cur
         cur.execute("SELECT fireID,lat,lon,dateObserved FROM allFires")
         out = []
         for c in cur:
             out.append([float(c[1]),float(c[2]),c[3]], int(c[0])) #order goes lat, lon, date, ID
         return out

    def deleteFires(self, fireID):
        cur = self.cur
        cur.execute("DELETE FROM allFires WHERE fireID = %s" %(fireID))
        self.cnx.commit()




if __name__ == "__main__":
    db = database()

    db.getFires()
    db.close()
