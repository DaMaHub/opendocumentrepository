# Open Document Repository


# Requirements

* Python 3
* running IPFS Daemon
* running Dogecoin core
* bottle
* ipfs-api
* libnacl >= 1.5.0

# Installing

For tests and developent, the system can be run from the terminal with 'python odr.py'. 
For deployment we use apache2 as wsgi server. See deploy.sh for an example.

# Running

Make sure you have a local IPFS daemon setup and running that can be reached 
by the wsgi process, or if you run it in development, by the user that runs the development.
You also need a local dogecoin core daemon setup and running. 


# Known Issues

* For some transactions, dogecoin core reports an "Internal Server Error". 
No idea what is happening there.
* Especially on MacOS X  libnacl fails to find libsodium. An alternative is
to just install it in the same directory where odr.py is situated.


# License

     Copyright (C) 2017 Ingo R. Keck for Kubrik Engineering / Open Knowledge Ireland

     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU Affero General Public License as
     published by the Free Software Foundation, either version 3 of the
     License, or (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU Affero General Public License for more details.

     You should have received a copy of the GNU Affero General Public License
     along with this program.  If not, see http://www.gnu.org/licenses/.

