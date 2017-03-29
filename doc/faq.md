# FAQ

(Based on e-mail excahnge with Eoghan Ó'Carragáin, UCC)

#### Q: I tried to install the project but it does not work anymore with the most up-to-date version of IPFS or py-ipfs-api. Why don't you fix the required version numbers?

A: IPFS is still a moving target and we noticed that old-version nodes tend to get moved out of the network quickly. So fixing a version will not help.


### 'Re the ODR setup, a few minor issues I ran into were: a dependency issue where pip installed the newer version of py-ipfs-api that you must be using. The module name has changed in the latest version, so I just did a find an replace for ipfsAPI to ipfsapi in odr.py and things started working'

A: IPFS is still alpha so changes like this happen quite often. It also does not help to force a defined IPFS version as the network tends to throw out old version nodes and only allows connections to up-to-date ones.

So we need to live with these problems and adapt. We will write tests for it but that needs taking care of a local ipfs daemon for the tests.

#### Q:  I kept getting a Directory not found error when uploading content until I figured out I needed to create a „temp" directory (maybe keep this in the repo with a .gitkeep?)

A: Fixed. temp directory will now be created if odr.py is run directly.

#### Q: I kept getting an KeyError when uploading/updating content. I got around this by commenting out the first half of the if block on lines 443 and 328. For me, the value of ref always seems to be in the form {'Hash' : 'Q....', 'Name': 'myname.txt' }, but the code seems to be expecting a different response format? Perhaps the result of another change in py-ipfs-api?

A: As you can see in the code: In the time I was working on it, the format already changed once. Seems they changed back to the old format now, but I messed up the detection switch. :-}

#### Q: I didn't have time to setup dogecoin. This meant the upload/update worked OK, but I got errors on browse/search because it couldn't find the txid. To be honest, I just hacked this to return dummy strings, just to get these pages working

A: Fixed. The uploading system was set up to ignore dogecoin problems, but the internal search engine wasn’t. Please delete the searchdb.json file before trying it out again.


### 'It was very cool to upload a file through the ODR and then retrieve it from the public ipfs gateway, but obviously this is already possible through the IPFS cli or "fancy webui". Of course, the ODR has some interesting elements over vanilla IPFS. I was particularly struck by the following (which I may be misunderstanding slightly)'

#### Q:  creating a blockchain transaction containing the IPFS hash (encrypted?) for both file contents and metadata objects. I assume this is partially to bake in a proof of existence type service. Also, from scanning the code, I assume it is possible to repopulate a fresh ODR instance with all relevant transactions from your personal dogecoin address (assuming the relevant objects are still pinned elsewhere on IPFS)?

A: That is the main idea. Image you have one ODR running on your main site of the organisation and now you want to get a new branch of your organisation on the other end of the world up and running with access to all documents. All you need to do is to start another instance on the new branch, and wait till it got everything synced. No interaction required. All you need for the setup is the dogecoin address where the messages are sent to, and the key pair wich is used to encrypt the messages.

You can force the repopulation by deleting the database („Delete local DB“) and reloading all from the blockchain meta-metadata (Reload DB) in the main menu.

Now in practice we have a problem that dogecoin does not inform us of new relevant transactions. And for real applications in this case you do not want a public permission-less blockchain, you want a public/private permissioned blockchain. So ODR right now is very much a technology demonstrator and a way to get valuable experiences.

The next step will be to re-design the whole system based on the experiences and using a better suited blockchain. We can for example use namecoin for an open system and use some tendermint implementation or LYSK for a closed system. I am working on a simple python blockchain as well.

#### Q:  writing the metadata as a discrete IPFS object (with its own dogecoin tx too)

A: Metadata can change, while the data can stay the same. Should we see it as a new document version if the metadata changes? We started out with „No“ but now I think it should be „yes“

#### Q:  Maintaining a simple version history by grouping ipfs hashes by the common/initial docid stored in metadata

A: In theory once ipfs has incorporated a version management we could use that. Plans are to use a git like approach, but to me it seems it is better to take what is working right now than to wait.

#### Q:   are there other large components/features I’ve over looked?

A: We only serve our own documents via the local IPFS-webgateway.

#### Q:  These are interesting features & I'd be interested in understanding more about the design choices.

A: A few queries/observations:

#### Q:  The UI only allows individual file uploads at present, I assume the intention is to allow folder upload and to make more of IPFS links in the future

A: Upload via the webinterface is a problem, so actually the best solution would be to upload locally via IPFS and just take the hash IPFS reports back. Now that IPFS exists written in Javascript that solution is actually do-able without a local install! Webserver upload would then be a fallback for clients that cannot run IPFS in the browser.

#### Q:  ODR doesn't currently seem to make much (any?) use of IPNS or IPLD. Do you have plans to incorporate these more, e.g. would there be a benefit in using an IPNS hash instead of the initial docid to group versions?

A: IPNS has the restriction (or at least had it the last time I was looking) that it only had one key per IPFS node. It also allows only one daemon running per machine and to make things worse access to the daemon is restricted to the user that started it. At the same time we have perfectly fine authentication possibilities without that restrictions via the blockchain that we need to run anyway. So IPNS would be a bad choice for us here in my eyes.

IPLD is very interesting and we are following the development. I do not really see a clear path how to separate or safely combine IPLD based reference information from similar information in the metadata and from the blockchain, so for now I simply stay away from it. But we will need to look at that in the near future.

#### Q:  Where do the digital signatures fit into the system?

A: Provenance. You vouch for the authenticity of the document/data you upload. See it as if you stamp/sign a document before you put it into the archive.

#### Q:  Most importantly, I'd love to hear more about how you see DaMaHub integrating into day-to-day work patterns.  I'd love to see some community consensus within the research data space around: 
	a) posix-friendly, git-like workflow for research data (the dat project, git-lfs and to some extent the new ipfs-pack address this but none are ideal); 
	b) self-describing data packages (hence the interest in research objects, datapackes.json, etc.). I assumed DaMaHub was a separate system from ODR, aimed more at a) above. Is that correct or are ODR and DaMaHub one and the same at present? 

A: ODR is a prototype for the public part of the DaMaHub system. The private part that allows private data sync, versioning, meta data management and commenting is still to be develop. Also ODR needs to be adjusted to the requirements of DaMaHub. But the basic ideas from ODR fit the open data part of DaMaHub.

Regarding the workflow I doubt that you can get all scientists to use a git-like workflow. Our idea is to provide a frontend that is as simple as dropbox but with a mercurial workflow in the backend (because git is a vicious beast of interdependent modules with poorly known internal restrictions and dependencies, while mercurial is a single-file python based well designed beauty that can do all git does but a lot nicer and consistent - end of rant) that is normally handled by the system but there in its full power if you want to use it.

#### Q: Re the self-describing data packages, I’m interested in the way you are writing metadata records to IPFS and blockchain, but I don't see how this would help to make the content retrieved by IPFS hash itself more interoperable and reusable etc (i.e. if retrieved out of context of the ODR).

A: We plan to enforce data packaging then at the moment you want to share your data with colleagues so you have an incentive to do it right at the start, and so when you want to open up the data most of the meta data is already there in a good quality.

#### Q:  I'm not entirely clear on the security model at the moment since IPFS doesn't really provide authentication/encryption out-of-the-box. Is it security-by-obscurity or am I missing some big aspect of the system?

A: ODR as demonstrator has no security apart from the key used to encrypt the information on the blockchain. As it is meant to be an open system all that is on IPFS should be open anyway so there is no problem. For DaMaHub the institution that runs a node will need to authenticate its users that can upload data and vouch for them with the institutional key pair. The data on ipfs is still supposed to be openly licensed. Changes to the data are not a problem as each data unit is addressed with the hash (so changes will generate a new hash). The system only recognises data that has been references on the blockchain, and the authenticity of the blockchain messages is provided by the signatures of the publishing institution.

If you do not want your data to be public, do not upload it on IPFS. That is our position. Juan seems to believe that encrypted data will be fine on IPFS but I do not share that view (see discussion https://github.com/ipfs/notes/issues/146#issuecomment-243401911). What you can do is to put IPFS on a private network, but one node leaking to the public network is enough for you data to walk away. This is why in DaMaHub the private data is not stored on IPFS.

#### Q:   It occurred to me that the current ODR prototype might lend itself to being rewritten as a static/javascript web-application, e.g. the current db is just a json file, the search doesn't make use of an rdms or nosql backend (have you seen lunrjs?), permanent data-storage is on IPFS and blockchain. I think using jsipfs might cut out the need to separately install IPFS daemon, but I have no idea about dogecoin or other dependencies.

A: As long as the data is small it may be done in the browser, but our guess is that we will probably handle quite big datasets and terabytes of data per node.

I am not aware of anyone doing a real blockchain in the browser, though now that bittorrent runs in a browser as well it should be do-able. The consent algorithm and the node discovery might be a problem to solve, though. (see: https://medium.com/@ingokeck/introduction-what-is-a-blockchain-f22510332bff#.xmzlf4k8g)

####  'Just a random thought, but it would be neat to build the demo in such a way that the app itself was distributed entirely via IPFS without further config or sever setup!'

A: We really appreciate all your effort! Hope many things are clearer now. And please try out the fixes and tell me if it works fine now without hacks.

## Note: ODR started out as simple technology demonstration. Many design choices were made to get it up and running quickly and to get first experiences. Some things that work now in IPFS did not work a year ago. For the next version we will change quite a bit thanks to the experiences we gained.
