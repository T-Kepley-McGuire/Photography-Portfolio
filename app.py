from app import create_app

if __name__ == '__main__':
    # Create the Flask app
    app = create_app()

    # Run the app
    app.run(debug=True)
