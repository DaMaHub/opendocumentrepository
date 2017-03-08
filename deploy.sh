#! /bin/bash
#
# this is a deploy script for apache2 that will set up a /var/wsgi folder for wsgi scripts,
# saves the database and keys, removes old installs and re-deploys.
# It will not setup the python3 wsgi system in apache itself, you need to take care of that before.
# The system also needs an IPFS daemon running locally that can be accessed by the www-data user.
#
#
# do not stop on error
set +e
# create wsgi folder if not existing
mkdir /var/wsgi
# save old document database and keys and config
mv /var/wsgi/odr/searchdb.json ./
cp /var/wsgi/odr/dogecoinconf.json ./
cp /var/wsgi/odr/keyfile.json ./
# delete old install
rm -rf /var/wsgi/odr/
# re-deploy
mkdir /var/wsgi/odr
mv searchdb.json /var/wsgi/odr/
cp -r static /var/wsgi/odr/
cp -r templates /var/wsgi/odr/
cp -r *.py /var/wsgi/odr/
mkdir temp /var/wsgi/odr/temp
cp -r  *.wsgi /var/www/html/demos/odr/
cp dogecoinconf.json /var/wsgi/odr/
cp keyfile.json /var/wsgi/odr/
# make sure we have the python requirements
pip3 install -r requirements.txt
chown -R www-data:www-data /var/wsgi
chown -R www-data:www-data /var/www/html/demos/odr
service apache2 restart
