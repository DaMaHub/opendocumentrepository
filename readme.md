# Open Document Repository

A Network of distributed document storage server built upon IPFS and Blockchain.

# Introduction

Imagine you have a world-wide organisation. All the documents that this organisation creates 
should be stored in a save and distributed way. All changes on one part of the world should be instantenously 
mirrored to all other parts of the world. All changes should be tracked and authentic. Documents 
should be stored with many copies in the network so that they are kept save (LOCKSS).

This is the idea behind this project.

# How does it work?

All documents and the metadata get saved on IPFS (https://ipfs.io). All links to the metadata and to the documents
are encrypted and saved to a blockchain. All nodes track the blockchain and retrieve all new documents and metadata
from IPFS.

If one node goes down, there are plenty of copies in the network. A new node just needs to read the blockchain and retrieve all
published data to be quickly up to date again.

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

Please see also the FAQ in the doc folder.

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

