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

print("Removal complete")