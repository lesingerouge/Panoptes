from webapp import create_app

app = create_app('dev')

if __name__ == "__main__":
	app.run("0.0.0.0",port=5050)
	
