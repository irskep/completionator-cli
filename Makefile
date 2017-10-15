.PHONY: deploy

deploy:
	python -m completionator --html --update > build/index.html
	ghp-import -np build
