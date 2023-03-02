from flask import Flask, render_template,  url_for
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import time
from threading import Thread

# Define the database connection string
db_string = "mysql+pymysql://newuser:password@localhost/meteostanica"

# Define a base object to use for defining the database schema
Base = declarative_base()

# Define the database schema for the sensors_data table
class SensorsData(Base):
    __tablename__ = "sensors_data"

    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    temperature2 = Column(Float)
    humidity = Column(Float)
    humidity2 = Column(Float)
    time = Column(DateTime)

# Define the database schema for the outside_sensors_data table
class OutsideSensorsData(Base):
    __tablename__ = "outside_sensors_data"

    id = Column(Integer, primary_key=True)
    temp = Column(Float)
    humidity = Column(Float)
    feelslike = Column(Float)
    snow = Column(Float)
    snowdepth = Column(Float)
    windspeed = Column(Float)
    pressure = Column(Float)
    uvindex = Column(Float)
    sunrise = Column(DateTime)
    sunset = Column(DateTime)
    moonphase = Column(Float)
    time = Column(DateTime)

# Define the database schema for the average table
class Average(Base):
    __tablename__ = "average"

    id = Column(Integer, primary_key=True)
    temp_indoors = Column(Float)
    temp_outdoors = Column(Float)
    humidity_indoors = Column(Float)
    humidity_outdoors = Column(Float)

# Create an engine object to connect to the database
engine = create_engine(db_string)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)

# Create a Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Serve the pocasie.html file
@app.route('/')
def index():
    css_file = url_for('static', filename='style.css')
    return render_template('pocasie.html', css_file=css_file)

# Define the function to fetch and emit the latest values
def emit_latest_values():
    while True:
        with Session() as session:
            # Fetch the latest values from each table
            latest_sensors_data = session.query(SensorsData).order_by(SensorsData.id.desc()).first()
            latest_outside_sensors_data = session.query(OutsideSensorsData).order_by(OutsideSensorsData.id.desc()).first()
            latest_average_data = session.query(Average).order_by(Average.id.desc()).first()

# Extract the values from the latest data, or None if no data exists
            indoor_temp_1 = latest_sensors_data.temperature if latest_sensors_data else None
            indoor_temp_2 = latest_sensors_data.temperature2 if latest_sensors_data else None
            indoor_humidity_1 = latest_sensors_data.humidity if latest_sensors_data else None
            indoor_humidity_2 = latest_sensors_data.humidity2 if latest_sensors_data else None
            outdoor_temp = latest_outside_sensors_data.temp if latest_outside_sensors_data else None
            outdoor_humidity = latest_outside_sensors_data.humidity if latest_outside_sensors_data else None
            outdoor_feelslike = latest_outside_sensors_data.feelslike if latest_outside_sensors_data else None
            outdoor_snow = latest_outside_sensors_data.snow if latest_outside_sensors_data else None
            outdoor_snowdepth = latest_outside_sensors_data.snowdepth if latest_outside_sensors_data else None
            outdoor_windspeed = latest_outside_sensors_data.windspeed if latest_outside_sensors_data else None
            outdoor_pressure = latest_outside_sensors_data.pressure if latest_outside_sensors_data else None
            outdoor_uvindex = latest_outside_sensors_data.uvindex if latest_outside_sensors_data else None
            outdoor_sunrise = latest_outside_sensors_data.sunrise if latest_outside_sensors_data else None
            outdoor_sunset = latest_outside_sensors_data.sunset if latest_outside_sensors_data else None
            outdoor_moonphase = latest_outside_sensors_data.moonphase if latest_outside_sensors_data else None
            average_temp_indoors = latest_average_data.temp_indoors if latest_average_data else None
            average_temp_outdoors = latest_average_data.temp_outdoors if latest_average_data else None
            average_humidity_indoors = latest_average_data.humidity_indoors if latest_average_data else None
            average_humidity_outdoors = latest_average_data.humidity_outdoors if latest_average_data else None

        # Emit the latest values to the 'values' event
        socketio.emit('values', {
            'indoor_temp_1': indoor_temp_1,
            'indoor_temp_2': indoor_temp_2,
            'indoor_humidity_1': indoor_humidity_1,
            'indoor_humidity_2': indoor_humidity_2,
            'outdoor_temp': outdoor_temp,
            'outdoor_humidity': outdoor_humidity,
            'outdoor_feelslike': outdoor_feelslike,
            'outdoor_snow': outdoor_snow,
            'outdoor_snowdepth': outdoor_snowdepth,
            'outdoor_windspeed': outdoor_windspeed,
            'outdoor_pressure': outdoor_pressure,
            'outdoor_uvindex': outdoor_uvindex,
            'outdoor_sunrise': outdoor_sunrise,
            'outdoor_sunset': outdoor_sunset,
            'outdoor_moonphase': outdoor_moonphase,
            'average_temp_indoors': average_temp_indoors,
            'average_temp_outdoors': average_temp_outdoors,
            'average_humidity_indoors': average_humidity_indoors,
            'average_humidity_outdoors': average_humidity_outdoors
        })
        print(f"Data sent: {indoor_temp_1}, {indoor_temp_2}, {indoor_humidity_1}, {indoor_humidity_2}, {outdoor_temp}, {outdoor_humidity}, {average_temp_indoors}, {average_temp_outdoors}, {average_humidity_indoors}, {average_humidity_outdoors},{outdoor_sunrise},{outdoor_sunset}}}")
        # Wait for 20 seconds before checking again
        time.sleep(20)


if __name__ == '__main__':
    socketio.start_background_task(target=emit_latest_values)

    # Start the SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


