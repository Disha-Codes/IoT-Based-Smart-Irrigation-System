# IoT-Based Smart Irrigation System

This is an intelligent irrigation system that uses **IoT sensors + Machine Learning + Cloud API** to automate watering decisions for crops. The system monitors real-time environmental conditions and predicts whether irrigation is needed and for how long.

# Project Overview

This project integrates:
 **ESP32 Microcontroller** for real-time data collection
**Sensors** (Soil Moisture, Temperature, Humidity)
**Machine Learning Models** for decision-making
**Flask API** for predictions
**Blynk App** for remote monitoring & control

The system supports both:
**Automatic Mode (AI-based irrigation)**
**Manual Mode (user-controlled irrigation)**

# Features
* Real-time sensor monitoring
* AI-based irrigation decision (Water / No Water)
* Irrigation duration prediction
* Manual pump control via mobile app
* Auto shut-off after predicted duration
* Model retraining support
* Live data visualization using Blynk


# Tech Stack

**SOFTWARE**
* Python
* Flask
* Scikit-learn
* Pandas
* NumPy
* Joblib

**HARDWARE**
* ESP32
* DHT22 Sensor
* Soil Moisture Sensor
* Relay Module (Pump Control)

**IoT Platform**
* Blynk


## 🖥️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/smart-irrigation.git
cd smart-irrigation
```

### 2️⃣ Install Dependencies

```bash
pip install pandas numpy scikit-learn flask joblib matplotlib
```

### 3️⃣ Train Models

```bash
python backend/iot.py
```

### 4️⃣ Run Flask Server

```bash
python backend/server.py
```

Server will run on:

```
http://0.0.0.0:5000
```

### 5️⃣ Upload ESP32 Code

* Open `.ino` file in Arduino IDE
* Update:

  * WiFi credentials
  * Flask server IP
* Upload to ESP32

## 📱 Blynk Controls

| Virtual Pin | Function         |
| ----------- | ---------------- |
| V0          | Soil Moisture    |
| V1          | Temperature      |
| V2          | Humidity         |
| V3          | Manual Pump      |
| V4          | Crop Type        |
| V5          | Growth Stage     |
| V6          | Auto/Manual Mode |


## ⚠️ Important Notes

* Ensure ESP32 and Flask server are on the same network
* Update IP address in `.ino` file:

```cpp
const char* serverName = "http://YOUR_IP:5000/predict";
```
* Update blynk credentials and wifi credentials in '.ino' file
## 👩‍💻 Authors

**Disha Desai**,
**Sharvani Surve**,
**Aastha Kamble**,
**Vaishnavi Bavkar**

## License

This project is for academic and educational purposes.
