from app import socketio, app

# Start the app
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=33507)
