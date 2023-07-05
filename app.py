from flask import Flask,render_template, request, redirect  
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tool.db'
db = SQLAlchemy(app)


# Route for retrieving weather data
@app.route('/weather', methods = ['GET', 'POST'])
def weather():
    if request.method == 'POST':    
        city_name = request.form['city']
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=643cafea114635a676a974102c10c69e'
        response = requests.get(url.format(city_name)).json()
        # Check the response status code
        if response['cod'] != 200:
            error_message = response['message']
            return render_template('weather.html', error_message=error_message)
        # Extract relevant weather data from the response
        temp = response['main']['temp']
        atm = response['weather'][0]['description']
        min_temp = response['main']['temp_min']
        max_temp = response['main']['temp_max']
        icon = response['weather'][0]['icon']
        # Render the weather template with the retrieved data
        return render_template('weather.html', temp=temp, atm=atm, min_temp=min_temp, max_temp=max_temp, icon=icon, city_name=city_name)
    # Render the weather template for GET requests
    return render_template('weather.html')


# Define the Device model
class Device(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    desc = db.Column(db.Integer, nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

with app.app_context(): # Create the database tables
    db.create_all()

# Home route for adding devices and displaying existing devices
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == "POST":
        title = request.form['title']
        desc = request.form['desc']
        # Validate if the desc value is numeric
        if not desc.isnumeric():
            error = "Tool Measurement must be a numeric value."
            allTool = Device.query.all()
            return render_template('index.html', allTool=allTool, error=error)
        # Create a new Device object and add it to the database
        tool = Device(title = title, desc = desc)
        db.session.add(tool)
        db.session.commit()
    # Retrieve all devices and render the index template
    allTool = Device.query.all()
    return render_template('index.html', allTool =  allTool)

# Update route for modifying device details
@app.route('/update/<int:sno>', methods = ['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        # Validate if the desc value is numeric
        if not desc.isnumeric():
            custom_error = "Tool Measurement must be a numeric value."
            tool = Device.query.filter_by(sno=sno).first()
            return render_template('update.html', tool=tool, custom_error=custom_error)
        # Retrieve the device, update its details, and commit changes
        tool = Device.query.filter_by(sno=sno).first()
        tool.title = title
        tool.desc = desc
        db.session.add(tool)
        db.session.commit()
        return redirect('/')
    tool = Device.query.filter_by(sno=sno).first()
    return render_template('update.html', tool =  tool)

# Delete route for removing a device
@app.route('/delete/<int:sno>')
def delete(sno):
    # Retrieve the device, delete it from the database, and commit changes
    tool = Device.query.filter_by(sno=sno).first()
    db.session.delete(tool)
    db.session.commit()
    # Redirect to the home page after successful deletion
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=8000)