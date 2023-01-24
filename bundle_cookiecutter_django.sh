#!/bin/sh

echo "Download repositories"
curl -k https://codeload.github.com/HenryJobst/cookiecutter-django-for-djlc/zip/refs/heads/master --output master.zip

mkdir -p ./project/static/project/zip_templates
mkdir -p tmp
unzip -u master -d tmp
rm master.zip
mv ./tmp/cookiecutter-django-for-djlc-master ./tmp/cookiecutter-django-for-djlc
cd tmp
zip -r cookiecutter-django-for-djlc.zip cookiecutter-django-for-djlc
rm -rf cookiecutter-django-for-djlc
mv cookiecutter-django-for-djlc.zip ../project/static/project/zip_templates
