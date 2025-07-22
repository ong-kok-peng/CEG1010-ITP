import os
from flask import Flask, request, jsonify
import serial
import time
import default_and_proficiency
import subprocess
import random

app = Flask(__name__)

SCOPES = ["/dev/ttyC1", "/dev/ttyC2", "/dev/ttyD1", "/dev/ttyD2"]
# CHANGE LABEL_TO_PORT ACCORDINGLY
LABEL_TO_PORT = {
    "C1": "/dev/ttyC1",
    "C2": "/dev/ttyC2",
    "D1": "/dev/ttyD1",
    "D2": "/dev/ttyD2",
}
BAUD_RATE = 9600
TIMEOUT = 1


def get_serial_connection(label):
    try:
        port = LABEL_TO_PORT[label]
        ser = serial.Serial(port, baudrate=BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)
        return ser
    except Exception as e:
        print(f"[ERROR] Could not open {label} ({LABEL_TO_PORT.get(label)}):", e)
        return None


@app.route('/', methods=['GET'])
def root():
    oscilloscopes_row = "C1-C2-D1-D2" #change accordingly i.e. G3-H3-G4-H4
    return jsonify({
        "status": "ok",
        "osc_row": oscilloscopes_row,
        "message": f"Oscilloscopes {oscilloscopes_row} is active."
    })


@app.route('/idn', methods=['GET'])
def get_idn():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})
    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})
    try:
        ser.write(b"*IDN?\n")
        time.sleep(0.1)
        response = ser.readline().decode().strip()
        ser.close()
        return jsonify({"status": "success", "label": label, "id": response})
    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})


@app.route('/autoset', methods=['GET'])
def autoset():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})
    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})
    try:
        ser.write(b":AUTOSet\n")
        ser.close()
        return jsonify({"status": "success", "message": f"AUTOSET command sent to {label}"})
    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})


@app.route('/set_coupling', methods=['GET'])
def set_coupling():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})
    ch = request.args.get("channel")
    mode = request.args.get("mode").upper()
    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})
    try:
        cmd = f"CHANnel{ch}:COUPling {mode}\n"
        ser.write(cmd.encode())
        ser.close()
        return jsonify({"status": "success", "message": f"Coupling set to {mode} on CH{ch} ({label})"})
    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})


@app.route('/get_coupling', methods=['GET'])
def get_coupling():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})
    ch = request.args.get("channel")
    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})
    try:
        cmd = f"CHANnel{ch}:COUPling?\n"
        ser.write(cmd.encode())
        time.sleep(0.1)
        response = ser.readline().decode().strip()
        ser.close()
        return jsonify({"status": "success", "label": label, "channel": ch, "coupling": response})
    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})


@app.route('/default', methods=['GET'])
def apply_default():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})
    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})
    try:
        default_and_proficiency.default_settings(ser)
        ser.close()
        return jsonify({"status": "success", "message": f"Default settings applied to {label}"})
    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/proficiency', methods=['GET'])
def apply_proficiency():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})
    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})
    try:
        default_and_proficiency.proficiency_test(ser)
        ser.close()
        return jsonify({"status": "success", "message": f"Proficiency test settings applied to {label}"})
    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})


@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        subprocess.Popen(["sudo", "shutdown", "now"])
        return jsonify({"status": "ok", "message": "Raspberry Pi is shutting down..."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/scramble', methods=['GET'])
def scramble_settings():
    label = request.args.get("label")
    if label not in LABEL_TO_PORT:
        return jsonify({"status": "error", "message": "Invalid oscilloscope label."})

    ser = get_serial_connection(label)
    if not ser:
        return jsonify({"status": "error", "message": f"{label} unavailable"})

    try:
        # Random vertical scale (0.2 to 5.0)
        vscale = random.choice([0.2, 0.5, 1.0, 2.0, 5.0])
        ser.write(f":CHAN1:SCAL {vscale}\n".encode())

        # Random time base (1ms to 500us)
        tscale = random.choice([1e-3, 5e-4, 2e-3])
        ser.write(f":TIM:SCAL {tscale}\n".encode())

        # Random coupling: DC, AC, or GND
        coupling = random.choice(["DC", "AC", "GND"])
        ser.write(f":CHAN1:COUP {coupling}\n".encode())

	# Randomize channel display states for CH1 to CH4
        for ch in range(1, 5):
            state = "OFF" if random.choice([True, False]) else "ON"
            ser.write(f":CHAN{ch}:DISP {state}\n".encode())

        ser.close()
        return jsonify({"status": "success", "message": f"Scrambled settings for {label}"})

    except Exception as e:
        ser.close()
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    print("[✓] Oscilloscope server running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)
