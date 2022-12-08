import numpy as np

import sqlalchemy
import datetime as DT
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation Measurements: /api/v1.0/precipitation<br/>"
        f"Station List: /api/v1.0/stations<br/>"
        f"Temperature for Previous Year: /api/v1.0/tobs<br/>"
        f"Temperature for Date: (yyyy-mm-dd): /api/v1.0/Start<br/>"
        f"Temperature for Start to End Dates (yyyy-mm-dd/yyyy-mm-dd): /api/v1.0/Start/End"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(measurement).order_by(measurement.date.desc()).first()
    starting_date = DT.datetime.strptime(most_recent_date.date, '%Y-%m-%d').date()
    previous_year = starting_date - DT.timedelta(days=365)
    query_result = session.query(measurement.date, measurement.prcp).filter(measurement.date >= previous_year).all()
    session.close()

    precipitation = []
    for date, prcp in query_result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():

    # Create a session from python to the DB
    session = Session(engine)
    station_queries = session.query(station.name, station.station, station.elevation).all()
    session.close()
    #create dictionary of stations
    list_of_stations = []
    for result in station_queries:
        row = {}
        row["name"] = result[0]
        row["station"] = result[1]
        row["elevation"] = result[2]
        list_of_stations.append(row)
      # Return a json list of stations
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from python to the DB
    session = Session(engine)
    # Starting from the most recent data point in the database.
    most_recent_date = session.query(measurement).order_by(measurement.date.desc()).first()
    starting_date = DT.datetime.strptime(most_recent_date.date, '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    previous_year = starting_date - DT.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    data_precip_scores = session.query(measurement.date, measurement.tobs).filter(measurement.date >= previous_year).all()
     # Close Session
    session.close()
    # Create a list of dictionaries with the date and temperature with for loop
    all_temperatures = []
    for date, temp in data_precip_scores:
        temp_information = {}
        temp_information['Date'] = date
        temp_information['Temperature'] = temp
        all_temperatures.append(temp_information)
    return jsonify(all_temperatures)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    query_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    tobs_all = []
    for min,avg,max in query_results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

@app.route('/api/v1.0/<start>/<end>')
def start_stop(start,end):
    session = Session(engine)
    query_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    tobs_all = []
    for min,avg,max in query_results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

if __name__ == '__main__':
    app.run(debug=True)