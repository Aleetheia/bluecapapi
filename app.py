from flask import Flask, request
from flask_restplus import Resource, Api
from flask import make_response

import json
import MySQLdb as sql
import pandas as pd
import math

app = Flask(__name__)
api = Api(app)

@api.route('/taux/<string:rasp>')
class taux_par_heure(Resource):
    def get(self,rasp):

        db = sql.connect(host='us-cdbr-iron-east-05.cleardb.net', database='heroku_8ed35d7a87fe1ad', user='b99b4e9fb9ac2b', password='8cf9b237')

        cursor = db.cursor()
        cursor.execute("SELECT num_desks FROM raspberries WHERE rasp_id = %s", [rasp])  
        row = cursor.fetchone()
        desks = (row[0])
        cursor.close()

        df = pd.read_sql('SELECT rasp_id,date,counter FROM counter_values WHERE rasp_id=%s', db, params = [rasp])  

        df['date'] = pd.to_datetime(df['date'])  
        df = df.set_index('date').resample('H')['counter'].max()  
        df = df.fillna(0)

        taux=[]
        for x in range(len(df)):
            taux.append(math.ceil(100*((df[x].sum()/desks))))

        hour =(pd.to_datetime(df.index)).strftime('%Y-%m-%d %H:%M:%S')       
        d = dict(zip(hour, taux))
        jsonarray = json.dumps(d)

        return (jsonarray)

    
@api.route('/raspberries')   
class liste_raspberries(Resource):
    def get(self):

        db = sql.connect(host='us-cdbr-iron-east-05.cleardb.net', database='heroku_8ed35d7a87fe1ad', user='b99b4e9fb9ac2b', password='8cf9b237')

        cursor = db.cursor()
        cursor.execute("SELECT rasp_id FROM raspberries") 
        
        raspberries = []
        for row in cursor:
            raspberries.append(row)
            
        return (raspberries)    
    


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#api.add_resource(taux_par_heure, '/taux/<string:rasp>')
#api.add_resource(liste_raspberries, '/raspberries')

if __name__ == '__main__':
     app.run()