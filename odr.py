# Open Document Repository, a demonstration of Blockchain and IPFS
#
# Copyright (C) 2017 Ingo R. Keck for Kubrik Engineering / Open Knowledge Ireland
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import bottle
import os
import json
import copy
import random
import datetime
import ipfsApi
import time
import blockchaincom


class MetaData(object):
    """our metadata superclass
       .metadata is a dict of dicts for each metadata value with its id as key and the following subkeys:
       "value" its value as a string
       "name" its name
       "datatype" its datatype with further info in .metadata_types
       metadata_types is a dict with infos for the metadata types interpretation
       important is the key "prettyprint", wich must be of the form "xyz %s jjj %s" where %s is
       going to be replaced by the metadata's value.
       """
    def __init__(self):
        self.metadata = dict()
        self.metadata_types = dict()
        #todo: define all types here together with their meta information
        self.metadata_types['author'] = dict()
        self.metadata_types['author']['prettyprint'] = '<i>Author:</i> %s, <br>'
        self.metadata_types['changes'] = dict()
        self.metadata_types['changes']['prettyprint'] = '<i>Changes:</i> %s, <br>'
        self.metadata_types['ipfsref'] = dict()
        self.metadata_types['ipfsref']['prettyprint'] = '</i> <a href="ipfsgateway/%s">%s</a> (local), <br>'
        self.metadata_types['blockchainref'] = dict()
        self.metadata_types['blockchainref']['prettyprint'] = '<i>Blockchain Reference:</i> <a href="bc_tx_get?txid=%s">%s</a></i><br>'
        self.metadata_types['date'] = dict()
        self.metadata_types['date']['prettyprint'] = '<i>Date:</i> %s, <br>'
        self.metadata_types['title'] = dict()
        self.metadata_types['title']['prettyprint'] = '<i>Title:</i> %s, <br>'
        self.metadata_types['keywords'] = dict()
        self.metadata_types['keywords']['prettyprint'] = '<i>Keywords:</i> %s, <br>'
        self.metadata_types['signature'] = dict()
        self.metadata_types['signature']['prettyprint'] = '<i>Signature:</i> %s, <br>'
        self.metadata_types['docid'] = dict()
        self.metadata_types['docid']['prettyprint'] = '<i>Document ID:</i> %s, <br>'
        self.metadata_types['filename'] = dict()
        self.metadata_types['filename']['prettyprint'] = '<i>Filename:</i> %s, <br>'
        self.metadata_types['relateddocs'] = dict()
        self.metadata_types['relateddocs']['prettyprint'] = '<i>Related documents:</i> %s, <br>'

    def pretty_print(self):
        """return a pretty print string of the metadata"""
        result = str()
        for item in self.metadata:
            eval_str = "'" + self.metadata_types[item['datatype']]['prettyprint'] + "' % ("
            for n in range(eval_str.count('%s')):
                eval_str += "item['value'],"
            eval_str = eval_str[0:-1] + ")\n"
            result += eval(eval_str)
        return result


class SearchEngine(object):
    """a simple search engine"""
    def __init__(self):
        self.db = dict()  # here we will save all the data
        self.db["keywords"] = dict()  # link from keyword to doc
        self.db["documents"] = dict()  # all doc references
        self.db["versions"] = dict()  # all verions for a docid
        #self.db["lastid"] = 0  # last used id in the portal - now we us ipfs hashes as id
        self.db["metadata"] = dict()
        self.dbfile = "searchdb.json"  # filename for persistent storage
        self.db["uploads"] = dict() # to limit number of uploads per day for demo

    def load_db(self):
        """load the db data from the file if it is not empty"""
        # try:
        #     if len(self.db["keywords"]) > 0:
        #         return False
        # except:
        #     pass
        # always load because we have multiple threads
        try:
            with open(self.dbfile, 'r') as f:
                self.db = json.load(f)
                f.close()
        except:
            return False
        return True

    def save_db(self):
        with open(self.dbfile, 'w') as f:
            json.dump(self.db, f)
            f.close()

    def add_keys(self, keylist, documentref, metadata, docid):
        """
        Add new keys to search engine. Docid is the ipfs of the 1. submitted doc.
        """
        # document as key, and track metadata independently
        for k in keylist:
            if k in self.db["keywords"]:
                self.db["keywords"][k].append(documentref)
            else:
                self.db["keywords"][k] = [documentref]
        self.db["documents"][documentref] = metadata
        if docid in self.db["versions"]:
            if documentref not in self.db["versions"][docid]:
                self.db["versions"][docid].append(documentref)
        else:
            self.db["versions"][docid] = [documentref]

    def find_match(self, key_list):
        if isinstance(key_list, str):
            key_list = self.str2keys(key_list)
        result = dict()
        for k in key_list:
            if k in self.db["keywords"]:
                for r in self.db["keywords"][k]:
                    if r in result:
                        result[r] += 1
                    else:
                        result[r] = 0
        matches = [w for w in sorted(result, key=result.get, reverse=True)]
        return matches

    def str2keys(self, keystring):
        """Help function: splits the keystring into key words, using , ; and whitespaces as splits"""
        alist = keystring.split(";")
        blist = []
        for k in alist:
            for i in k.split(","):
                for j in i.split():
                    blist.append(j.lower())
        return copy.deepcopy(blist)


class AppConstants(dict):
    """A simple dict class that gives configuration constants for the app"""
    def __init__(self):
        self['restrict uploads'] = True
        self['uploads per day'] = 40

    def test_upload(self, db):
        """Test if the daily limit is active and still uploads possible. True if upload is allowed."""
        if self['restrict uploads']:
            if datetime.date.today().isoformat() in db["uploads"]:
                if db["uploads"][datetime.date.today().isoformat()] < self['uploads per day']:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return True
    def increase_upload_counter(self, db):
        """increase the blokchain upload counter by 1"""
        if datetime.date.today().isoformat() in db["uploads"]:
            db["uploads"][datetime.date.today().isoformat()] += 1
        else:
            db["uploads"][datetime.date.today().isoformat()] = 1
        return db["uploads"][datetime.date.today().isoformat()]

app = bottle.Bottle()
app.se = SearchEngine()
app.constants = AppConstants()

# Static Routes
@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename, root='static/js')


@app.get('/<filename:re:.*\.(css|map)>')
def stylesheets(filename):
    return bottle.static_file(filename, root='static/css')


@app.get('/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename, root='static/img')


@app.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return bottle.static_file(filename, root='static/fonts')


@app.get('/ipfsgateway/<docid>')
def ipfsgateway(docid):
    """
    A simple IPFS gateway, that will only serve locally uploaded IPFS files (i.e. not access external files)
    :return: file
    """
    # first of all, clean directory
    clean_temp_files()
    # docid = bottle.request.query.id
    if docid:
        # get all local pinned ID
        # con = ipfsApi.Client('localhost', 5001)
        # all = list(con.refs_local()) # not yet implemented, so we will use the refs from the search engine instead
        #
        app.se.load_db()  # if our db is empty, try to load it from disk
        allrefs = list(app.se.db["documents"].keys())
        if docid in allrefs:
            # serve doc
            con = ipfsApi.Client('localhost', 5001)
            oldpath = os.getcwd()
            os.chdir(os.path.join(oldpath, "temp"))
            file_to_serve = []
            try:
                result = con.get(docid)
                print(result)
                documentfilename = app.se.db["documents"][docid]["filename"]
                docext = os.path.splitext(documentfilename)[-1]
                os.rename(docid, docid+docext)
                os.chdir(oldpath)
                file_to_serve = bottle.static_file(docid+docext, root='temp')
            except:
                pass
            finally:
                os.chdir(oldpath)
            return file_to_serve
        else:
            raise bottle.HTTPError(status=404, body="Not found", traceback=None)
    else:
        raise bottle.HTTPError(status=404, body="Not found", traceback=None)


@app.get('/upload')
def upload_page():
    if not app.constants.test_upload(app.se.db):  # test if daily upload limit reached
        return "Daily upload limit reached"
    return bottle.template('templates/upload.tpl')


@app.get('/update')
def update_page():
    if not bottle.request.query.docref:
        return "Document reference needed"
    else:
        app.se.load_db()
        docref = bottle.request.query.docref
        author = app.se.db["documents"][docref]["author"]
        category = app.se.db["documents"][docref]["category"]
        changes = app.se.db["documents"][docref]["changes"]
        keywords = app.se.db["documents"][docref]["keywords"]
        sigtext = app.se.db["documents"][docref]["signature"]
        docid = app.se.db["documents"][docref]["docid"]
    return bottle.template('templates/update.tpl', author=author, category=category, changes=changes,
                           keywords=keywords, sigtext=sigtext, docid=docid, docref=docref)


@app.post('/update')
def update_file():
    app.se.load_db()  # if our db is empty, try to load it from disk
    if not app.constants.test_upload(app.se.db):  # test if daily upload limit reached
        return "Daily upload limit reached"
    tempdir = 'temp'
    category = bottle.request.forms.get('category')
    checkbox = bottle.request.forms.get('ccheck')
    author = bottle.request.forms.get('author')
    keywords = bottle.request.forms.get('keywords')
    print(category, checkbox, author, keywords)
    upload = bottle.request.files.get('upload')
    docid = bottle.request.forms.get('docid')
    sigdata = bottle.request.forms.get('sigtext')
    changes = bottle.request.forms.get('changes')
    docref = bottle.request.forms.get('docref')
    name = ""
    # sname = ""
    ext = ""
    # sext = ""
    documentfilename = ""
    if not docid:
        return "Doc ID needed"
    blockchainref = app.se.db['documents'][docref]["blockchainref"] # get it from search database for now. later ipfs
    signature = bottle.request.files.get('signature')
    if signature:
        # signature file wins over sigdata text
        sname, sext = os.path.splitext(signature.filename)
        if sext.lower() not in ('.sig', '.signature'):
            return 'Signature file extension should be .sig or .signature. ' \
                   'Are you sure %s is a signature file?' % signature.filename
        # save sig file in temp dir
        print("saving signature file")
        signature.save('temp', overwrite=True)
        try:
            with open(os.path.join(tempdir, sname+sext), "r") as f:
                sigdata = f.read()
                f.close()
        except:
            return "Unable to read signature file %s" % signature.filename
        finally:
            os.remove(os.path.join(tempdir, sname + sext))
            signature.file.close()
    # save file in temp dir
    # documentref = "".join([str(random.randrange(0,9)) for i in range(15)])  # in case ipfs not working
    #blockchainref = "".join([str(random.randrange(0,9)) for i in range(15)])  # in case blockchain not working
    print("connect to ipfs")
    con = ipfsApi.Client('localhost', 5001)
    if upload:
        if not checkbox == "on":
            return "File upload is only possible if you own the rights to the document. " \
                   "Remember that it will be published to IPFS and thus will be " \
                   "accessible all over the world."
        name, ext = os.path.splitext(upload.filename)
        try:
            print("saving file")
            upload.save('temp', overwrite=True)
            print("adding file to ipfs")
            ref = con.add(os.path.join(tempdir, name + ext))
            if len(ref) > 1:
                docref = ref[0]['Hash']  # ipfs reference
                documentfilename = os.path.split(ref[0]['Name'])[-1]
            else:
                docref = ref['Hash'] # ipfs reference
                documentfilename = ref['Name']
            # pinn it
            print("pinning file to ipfs")
            con.pin_add(docref)

        finally:
            # delete temp file again
            os.remove(os.path.join(tempdir, name + ext))
            upload.file.close()
            if docid not in app.se.db['versions']:
                docid = docref
                #app.se.db["lastid"] += 1
        try:
            # save document reference on blockchain
            mymessage = "data:%s" % docref
            blockchainref = blockchaincom.save_on_dogecoin(mymessage) # we will have a new one
            app.constants.increase_upload_counter(app.se.db)  # increase daily upload counter
        except:
            print("blockchainupload failed")
    else:
        #app.se.load_db()  # if our db is empty, try to load it from disk
        if docref not in app.se.db['documents']:
            return "Existing Document IPFS reference is needed"

    newkeys = app.se.str2keys("%s, %s, %s, %s, %s" % (category, author, keywords,
                                                      name, ext))  # extract meta data keys

    if not documentfilename:
        documentfilename = app.se.db['documents'][docref]["filename"]
        name = app.se.db['documents'][docref]["title"]
    metadata = dict(category=category, author=author, keywords=keywords,
                    signature=sigdata, documentref=docref,
                    docdate=datetime.datetime.today().isoformat(),
                    docid=docid, title=name, changes=changes,
                    blockchainref=blockchainref, filename=documentfilename)
    app.se.add_keys(newkeys, docref, metadata, docid)  # this will also add the new ref as version
    # add metadata as ipfs object
    print("add metadata to ipfs")
    ref = con.add_pyobj(metadata)
    app.se.db["metadata"][docref] = ref
    try:
        # save metadata reference on blockchain
        mymessage = "meta:%s" % ref
        blockchain_ref = blockchaincom.save_on_dogecoin(mymessage)
        app.constants.increase_upload_counter(app.se.db) # increase daily upload counter
    except:
        print("blockchain metadata upload failed")
    print("save sedb")
    app.se.save_db()  # save search engine data
    return bottle.template('templates/upload_correct.tpl')


@app.post('/upload')
def upload_file():
    if not app.constants.test_upload(app.se.db):  # test if daily upload limit reached
        return "Daily upload limit reached"
    tempdir = 'temp'
    category = bottle.request.forms.get('category')
    checkbox = bottle.request.forms.get('ccheck')
    author = bottle.request.forms.get('author')
    keywords = bottle.request.forms.get('keywords')
    print(category, checkbox, author, keywords)
    upload = bottle.request.files.get('upload')
    docid = bottle.request.forms.get('docid')
    changes = ""
    # name = ""
    # sname = ""
    # ext = ""
    # sext = ""
    if not checkbox == "on":
        return "File upload is only possible if you own the rights to the document. " \
               "Remember that it will be published to IPFS and thus will be " \
               "accessible all over the world. (aka: you forgot to check the checkbox)"
    if not upload:
        return "Please select a file for uploading."
    name, ext = os.path.splitext(upload.filename)
    signature = bottle.request.files.get('signature')
    print("load sedb")
    app.se.load_db()  # if our db is empty, try to load it from disk
    newkeys = app.se.str2keys("%s, %s, %s, %s, %s" % (category, author, keywords,
                                                      name, ext))  # extract meta data keys
    sigdata = ""
    if signature:
        sname, sext = os.path.splitext(signature.filename)
        if sext.lower() not in ('.sig', '.signature'):
            return 'Signature file extension should be .sig or .signature. ' \
                   'Are you sure %s is a signature file?' % signature.filename
        # save sig file in temp dir
        print("saving signature file")
        signature.save('temp', overwrite=True)
        try:
            with open(os.path.join(tempdir, sname+sext), "r") as f:
                sigdata = f.read()
                f.close()
        except:
            return "Unable to read signature file %s" % signature.filename
        finally:
            os.remove(os.path.join(tempdir, sname+sext))
            signature.file.close()
    # save file in temp dir
    document_ref = "".join([str(random.randrange(0,9)) for i in range(15)])  # in case ipfs not working
    #blockchain_ref = "".join([str(random.randrange(0,9)) for i in range(15)])  # in case blockchain not working
    blockchain_ref = ["blockchain tx"]
    try:
        print("saving file")
        upload.save('temp', overwrite=True)
        print("connect to ipfs")
        con = ipfsApi.Client('localhost', 5001)
        print("adding file to ipfs")
        ref = con.add(os.path.join(tempdir, name + ext))
        if len(ref) > 1:
            document_ref = ref[0]['Hash']  # ipfs reference
            documentfilename = os.path.split(ref[0]['Name'])[-1]
        else:
            document_ref = ref['Hash'] # ipfs reference
            documentfilename = ref['Name']
        # pinn it
        print("pinning file to ipfs")
        con.pin_add(document_ref)
        #documentfilename = ref['Name']
    except:
        return("IPFS upload failed")
    finally:
        # delete temp file again
        os.remove(os.path.join(tempdir, name + ext))
        upload.file.close()
    try:
        # save document reference on blockchain
        mymessage = "data:%s" %document_ref
        blockchain_ref = blockchaincom.save_on_dogecoin(mymessage)
        app.constants.increase_upload_counter(app.se.db) # increase daily upload counter
    except:
        print("blockchainupload failed")
    if not docid:
        #docid = "%d" %(app.se.db['lastid']+1)
        docid = document_ref
    metadata = dict(category=category, author=author, keywords=keywords,
                    signature=sigdata, documentref=document_ref,
                    docdate=datetime.datetime.today().isoformat(),
                    docid=docid, title=name, changes=changes,
                    blockchainref=blockchain_ref, filename=documentfilename)
    app.se.add_keys(newkeys, document_ref, metadata, docid)
    #app.se.db["lastid"] += 1
    # add metadata as ipfs object
    print("add metadata to ipfs")
    ref = con.add_pyobj(metadata)
    app.se.db["metadata"][document_ref] = ref
    try:
        # save metadata reference on blockchain
        mymessage = "meta:%s" % ref
        blockchain_ref = blockchaincom.save_on_dogecoin(mymessage)
        app.constants.increase_upload_counter(app.se.db) # increase daily upload counter
    except:
        print("blockchain metadata upload failed")
    print("save sedb")
    app.se.save_db()  # save search engine data
    return bottle.template('templates/upload_correct.tpl')


@app.route('/browse')
def browse():
    app.se.load_db()  # if our db is empty, try to load it from disk
    # iterate over all doc ids in the database
    data = "<ul>\n"
    for docid in app.se.db['versions']:
        # get last document name as headline
        docref = app.se.db['versions'][docid][-1]
        headline = app.se.db["documents"][docref]["title"]
        # iterate over all document versions
        data += "<li><a href='document?id=%s'>%s</a>\n<ul>" %(docid,headline)
        for docref in app.se.db['versions'][docid]:
            newentry = "<li>\n"
            newentry += "<i>Date:</i> %s, <i>Title:</i> <a href='document?docref=%s'>%s</a><br> " \
                        "<i>Author:</i> %s, " \
                        "<i>Changes:</i> %s<br>" \
                        "<i>IFPS Reference:</i> <a href='ipfsgateway/%s'>%s</a> (local), <br>" \
                        "<i>Blockchain Reference:</i> <a href='bc_tx_get?txid=%s'>%s</a></i><br>" \
                        % (app.se.db["documents"][docref]["docdate"],
                            app.se.db["documents"][docref]["documentref"],
                            app.se.db["documents"][docref]["title"],
                            app.se.db["documents"][docref]["author"],
                            app.se.db["documents"][docref]["changes"],
                            app.se.db["documents"][docref]["documentref"],
                            app.se.db["documents"][docref]["documentref"],
                            app.se.db["documents"][docref]["blockchainref"][0]["txid"],
                            app.se.db["documents"][docref]["blockchainref"][0]["txid"])
            newentry += "</li>\n"
            data += newentry
        data += "</ul>\n"
    data += "</ul>\n"

    return bottle.template('templates/browse.tpl', data=data)


@app.route('/about')
def about():
    return bottle.template('templates/about.tpl')


@app.route('/document')
def document():
    app.se.load_db()  # if our db is empty, try to load it from disk
    if bottle.request.query.id:
        doctype = "Version"
        docid = bottle.request.query.id
        # return data for versions id
        # get last document name as headline
        docref = app.se.db['versions'][docid][-1]
        headline = app.se.db["documents"][docref]["title"]
        # iterate over all document versions
        data = "%s\n<ul>" % headline
        for docref in app.se.db['versions'][docid]:
            newentry = "<li>\n"
            newentry += "<a href='document?docref=%s'><i>Date:</i> %s, <br><i>Title:</i> %s</a><br> " \
                        "<i>Author:</i> %s,<br> " \
                        "<i>Changes:</i> %s,<br>" \
                        "<i>IFPS Reference:</i> <a href='ipfsgateway/%s'>%s</a> (local), <br> " \
                        "<i>ipfs.io URL:</i> "\
                        "<a href='https://ipfs.io/ipfs/%s'>https://ipfs.io/ipfs/%s</a> (external), <br>" \
                        "<i>Blockchain Reference:</i> <a href='bc_tx_get?txid=%s'>%s</a></i><br>" \
                        % (app.se.db["documents"][docref]["documentref"],
                           app.se.db["documents"][docref]["docdate"],
                           app.se.db["documents"][docref]["title"],
                           app.se.db["documents"][docref]["author"],
                           app.se.db["documents"][docref]["changes"],
                           app.se.db["documents"][docref]["documentref"],
                           app.se.db["documents"][docref]["documentref"],
                           app.se.db["documents"][docref]["documentref"],
                           app.se.db["documents"][docref]["documentref"],
                           app.se.db["documents"][docref]["blockchainref"][0]["txid"],
                           app.se.db["documents"][docref]["blockchainref"][0]["txid"])
            newentry += "</li>\n"
            data += newentry
        data += "</ul>\n"
    elif bottle.request.query.docref:
        doctype = "Document"
        docref = bottle.request.query.docref
        # return data for document reference
        data = ""
        data += "<i>Date:</i> %s, <br><i>Title:</i> <a href='ipfsgateway/%s'>%s</a><br> " \
                "<i>Author:</i> %s, <br>" \
                "<i>Changes:</i> %s <br>" \
                "<i>Keywords:</i> %s <br>"\
                "<i>Category:</i> %s <br>" \
                "<i>IFPS Reference:</i> <a href='ipfsgateway/%s'>%s</a> (local), <br> " \
                "<i>ipfs.io URL:</i> " \
                "<a href='https://ipfs.io/ipfs/%s'>https://ipfs.io/ipfs/%s</a> (external), <br>" \
                "<i>Blockchain Reference:</i> <a href='bc_tx_get?txid=%s'>%s</a></i><br>" \
                "<i>Signature:</i> %s " \
                % (app.se.db["documents"][docref]["docdate"],
                   app.se.db["documents"][docref]["documentref"],
                   app.se.db["documents"][docref]["title"],
                   app.se.db["documents"][docref]["author"],
                   app.se.db["documents"][docref]["changes"],
                   app.se.db["documents"][docref]["keywords"],
                   app.se.db["documents"][docref]["category"],
                   app.se.db["documents"][docref]["documentref"],
                   app.se.db["documents"][docref]["documentref"],
                   app.se.db["documents"][docref]["documentref"],
                   app.se.db["documents"][docref]["documentref"],
                   app.se.db["documents"][docref]["blockchainref"][0]["txid"],
                   app.se.db["documents"][docref]["blockchainref"][0]["txid"],
                   app.se.db["documents"][docref]["signature"])
    else:
        return bottle.redirect('/demos/odr/search')
    return bottle.template('templates/document.tpl', type=doctype, data=data, docref=docref)


@app.route('/')
def redir():
    try:
        if bottle.request.environ['PATH_INFO'][-1] == '/':
            return bottle.redirect('search')
        else:
            return bottle.redirect('/demos/odr/search')
    except IndexError:
        return bottle.redirect('/demos/odr/search')
    # return bottle.redirect('/')

@app.route('/delete_db')
def delete_db():
    try:
        # new search engine db
        app.se.load_db()
        uploads = app.se.db["uploads"]
        app.se = SearchEngine()
        app.se.db["uploads"] = uploads
        app.se.save_db()
    except:
        return('something went wrong, please try again.')
    return bottle.redirect('browse')

@app.route('/search')
def search():
    if bottle.request.query.keywords:
        keywordstr = bottle.request.query.keywords
        app.se.load_db()  # if our db is empty, try to load it from disk
        matches = app.se.find_match(keywordstr)
        # iterate over all doc ids in the database
        data = "<ul>\n"
        for docref in matches:
            # get last document name as headline
            # headline = app.se.db["documents"][docref]["title"]
            newentry = "<li>\n"
            newentry += "<i>Date:</i> %s, <i>Title:</i> <a href='document?docref=%s'>%s</a><br> " \
                            "<i>Author:</i> %s, " \
                            "<i>Changes:</i> %s<br>" \
                            "<i>IFPS Reference:</i> <a href='https://ipfs.io/ipfs/%s'>%s</a> (ipfs.io), " \
                            "<a href='ipfsgateway/%s'>%s</a> (local), " \
                            "<i>Blockchain Reference:</i> <a href='bc_tx_get?txid=%s'>%s</a></i>" \
                            % (app.se.db["documents"][docref]["docdate"],
                               app.se.db["documents"][docref]["documentref"],
                               app.se.db["documents"][docref]["title"],
                               app.se.db["documents"][docref]["author"],
                               app.se.db["documents"][docref]["changes"],
                               app.se.db["documents"][docref]["documentref"],
                               app.se.db["documents"][docref]["documentref"],
                               app.se.db["documents"][docref]["documentref"],
                               app.se.db["documents"][docref]["documentref"],
                               app.se.db["documents"][docref]["blockchainref"][0]["txid"],
                               app.se.db["documents"][docref]["blockchainref"][0]["txid"])
            newentry += "</li>\n"
            data += newentry
        data += "</ul>\n"
        return bottle.template('templates/searchresult.tpl', data=data)
    else:
        return bottle.template('templates/search.tpl')

@app.route('/bc_tx_get')
def blockchain_get_tx():
    if bottle.request.query.txid:
        txid = bottle.request.query.txid
        # retrieve ID from blockchain
        return blockchaincom.get_tx(txid)
    else:
        return "no transaction ID given"


def clean_temp_files(tempdir="temp", timedelta=600):
    """
    look for temporary files that are older than 10 minute and delete them

    """
    alltempfiles = os.listdir(tempdir)
    now = time.time()
    for file in alltempfiles:
        if (now-os.path.getmtime(os.path.join(tempdir,file))) > timedelta:
            os.remove(os.path.join(tempdir,file))


@app.route('/bootstrap')
def bootstrap():
    # new search engine db
    if VERBOSE:
        print("creating new database")
    app.se.load_db()
    uploads = app.se.db["uploads"]
    app.se = SearchEngine()
    app.se.db["uploads"] = uploads
    if VERBOSE:
        print("Get all references from Blockchain")
    # get all metadata from blockchain
    bc_data = blockchaincom.retrieve_from_dogecoin(blockchaincom.op_return_dogecoin.OP_RETURN_DOGECOIN_ADDRESS, VERBOSE=VERBOSE)
    #print(bc_data)
    if VERBOSE:
        print("Get all data from IPFS")
    con = ipfsApi.Client('localhost', 5001)
    added_keys="<ul>"
    for message in bc_data:
        if VERBOSE:
            print("working on message %s" % message[0].decode('latin1'))
        try:
            dtype, dhash = message[0].decode('latin1').split(':')
        except:
            continue
        if dtype != 'meta':
            continue
        # get metadata
        try:
            if VERBOSE:
                print("Try to get hash %s from IPFS" % dhash)
            metadata = con.get_pyobj(dhash)
        except:
            print('Could not access pyobject %s' %dhash)
            continue
        #print(metadata)
        # add it to local search engine
        newkeys = metadata["category"] + ','
        newkeys += metadata["author"] + ','
        newkeys += metadata["keywords"] + ','
        newkeys += metadata["title"] + ','
        newkeys += os.path.splitext(metadata["filename"])[-1][1:] + ','
        newkeys = app.se.str2keys(newkeys) # extract meta data keys
        app.se.add_keys(keylist=newkeys, documentref=metadata["documentref"],metadata=metadata, docid=metadata["docid"])
        # save metadata ipfs
        app.se.db["metadata"][metadata["documentref"]] = dhash
        #pin it
        con.pin_add(dhash)
        #con.pin_add(metadata["documentref"])
        added_keys += "<li>" + "<a href='document?id=%s'>%s</a>" %(metadata["documentref"], dhash) + '</li>\n'
    #save db again
    added_keys += "</ul>"
    app.se.save_db()
    return bottle.template('templates/bootstrap.tpl', data=added_keys)


if __name__ == '__main__':
    MULTITHREAD = False
    VERBOSE = True
    if not MULTITHREAD:
        try:
            app.run(host='localhost', port=8081, debug=True, reloader=True)
        except:
            pass
        finally:
            app.close()
    else:
        from wsgiref.simple_server import make_server, WSGIServer
        from socketserver import ThreadingMixIn

        class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
            daemon_threads = True

        class Server:
            def __init__(self, wsgi_app, listen='127.0.0.1', port=8081):
                self.wsgi_app = wsgi_app
                self.listen = listen
                self.port = port
                self.server = make_server(self.listen, self.port, self.wsgi_app,
                                          ThreadingWSGIServer)

            def serve_forever(self):
                self.server.serve_forever()
        wsgiapp = app
        httpd = Server(wsgiapp)
        httpd.serve_forever()