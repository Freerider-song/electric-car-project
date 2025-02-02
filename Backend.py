import os
import urllib.parse as up
import psycopg2, datetime
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_restx import Api, Resource
from mapboxgl.utils import df_to_geojson
import json
import pandas as pd
#2021.11.09 김호송 수정 시작

app=Flask(__name__)
api = Api(app)

up.uses_netloc.append("postgres")
os.environ["DATABASE_URL"] = "postgres://yadctsip:mvZ_FWEhIcFp4PCZMlzUtdZivUkj1IBG@arjuna.db.elephantsql.com/yadctsip"
url = up.urlparse(os.environ["DATABASE_URL"])
connect = psycopg2.connect(database=url.path[1:],
                        user=url.username,
                        password=url.password,
                        host=url.hostname,
                        port=url.port)
cur = connect.cursor()
cur.execute("select * from Station")
data = cur.fetchall()
print(data)

@app.route('/CheckLogin', methods=['POST'])
def CheckLogin():
    id = request.args.get('Id')
    pw = request.args.get('Password')
    print(id, pw)
    cur.execute("select * from customer where customer_id='{}' and password='{}'".format(id, pw))
    data = cur.fetchall()
    if len(data) == 1:
        return jsonify({'result_code': 1})
    else:
        return jsonify({'result_code': 0})

@app.route('/GetMemberInfo', methods=['POST'])
def GetMemberInfo():
    id = request.args.get('Id')
    cur.execute("select * from customer where customer_id='{}'".format(id))
    data = cur.fetchall()
    name = data[0][2]
    car_model = data[0][3]

    return jsonify({'name': name,
                    'car_models': car_model})

@app.route('/GetCarInfo', methods=['POST'])
def GetChargeResult():
    id = request.args.get('Id')
    cur.execute("select * from ServiceReservation where customer_id='{}".format(id))
    data = cur.fetchall()[-1]
    current_capacity = '몰라'
    seq_reserve = data[0]
    reserve_type = data[6]
    reserve_time = data[3]
    finish_time = data[4]
    min_capacity = data[5]

    return jsonify({
        'current_capacity': current_capacity,
        'seq_reserve': seq_reserve,
        'reserve_type': reserve_type,
        'reserve_time': reserve_time,
        'finish_time': finish_time,
        'min_capacity': min_capacity
    })


@app.route('/SetSignUpInfo', methods=['POST'])
def SetSignUpInfo():
    name = request.args.get('Name')
    id = request.args.get('Id')
    pw = request.args.get('Password')
    car_model = request.args.get('Car_model')
    try:
        cur.execute("insert into customer values('{}','{}','{}','{}')".format(id, pw, name, car_model))
        connect.commit()
        return jsonify({'result_code': 1})
    except:
        return jsonify({'result_code': 0})

@app.route('/GetCarCompanyInfo', methods=['POST'])
def GetCarCompanyInfo():
    dict_ = {}
    cur.execute("select distinct manufacturer from carmodel")
    data = cur.fetchall()



@app.route('/GetCarModelInfo', methods=['POST'])
def GetCarModelInfo():
    dict_ = {}
    company = request.args.get('Car_company')
    cur.execute("select car_model from CarModel where manufacturer='{}'".format(company))
    data = cur.fetchall()
    for i in range(len(data)):
        dict_["model_{}".format(i)] = data[i][0]
    return jsonify(dict_)

@app.route('/GetStationInfo', methods=['POST'])
def GetStationInfo():
    dict_ = {}
    cur.execute("select station_id, station_name, slow_charger, fast_charger, dx, dy")
    data = cur.fetchall()
    data = pd.DataFrame(data, columns=['station_id', 'station_name', 'slow_charger', 'fast_charger', 'dx', 'dy'])
    geo_data = df_to_geojson(
        df=data,
        properties=['station_id', 'station_name', 'slow_charger', 'fast_charger'],
        lat='dx',
        lng='dy',
        precision=5,
        filename='station.geojson'
    )
    path = 'station.geojson'
    with open(path) as f:
        data = json.loads(f.read())
        print(1)
    return data




if __name__ == "__main__":
    app.run(Debug=True, host='0.0.0.0')


