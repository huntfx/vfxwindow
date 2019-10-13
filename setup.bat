IF EXIST dist (rmdir dist /s /q)
python setup.py sdist
python -m twine upload dist/*
rmdir dist /s /q