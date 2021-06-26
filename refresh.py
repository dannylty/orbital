import os

if __name__ == "__main__":
	try:
		os.remove("db.sqlite3")
	except:
		print("db removed alr bro")

	for root, dirs, files in os.walk("main/migrations"):
		for name in files:
			if name != "__init__.py":
				os.remove(os.path.join(root, name))

	for file in os.listdir("main/migrations/__pycache__"):
		os.remove(os.path.join("main/migrations/__pycache__", file))

	for file in os.listdir("main/__pycache__"):
		if file != "__init__.cpython-39":
			os.remove(os.path.join("main/__pycache__", file))

	for file in os.listdir("orbital/__pycache__"):
		if file != "__init__.cpython-39":
			os.remove(os.path.join("orbital/__pycache__", file))

print("Removal complete")