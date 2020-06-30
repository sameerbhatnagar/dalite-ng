test:
	pytest --nomigrations --cov --cov-report term-missing
test-cdb:
	pytest --nomigrations --cov --cov-report term-missing --create-db
rebuild:
	./node_modules/gulp/bin/gulp.js build
	./manage.py collectstatic --clear --noinput
	./manage.py compress
refresh: rebuild
	./manage.py runserver
