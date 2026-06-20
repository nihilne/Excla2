.PHONY: build-css watch

build-css:
	tailwindcss -i ./public/static/css/input.css -o ./public/static/css/styles.css

watch:
	tailwindcss -i ./public/static/css/input.css -o ./public/static/css/styles.css --watch
