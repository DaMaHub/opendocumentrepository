<!DOCTYPE html>
<html lang="en">
% include('templates/header.tpl', title='Kubrik.io Open Document Proof Of Concept')

  <body>

% include('templates/navbar.tpl')

    <div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="page-header" style="padding-top:40px;">
        <h1>Update Document</h1>
      </div>
        <div class="row marketing">
        <div class="col-lg-6">
        <p>Here you can update a document in the repository</p>
        <p>
        </p>
          <form action="update" method="post" enctype="multipart/form-data">
            <div class="form-group">
              <label for="category">Category:</label>
              <input type="text" id="category" name="category" class="form-control" value="{{category}}"/>
            </div>
            <div class="form-group">
              <label for="author">Author:</label>
              <input type="text" id="author" name="author" class="form-control" value="{{author}}"/>
            </div>
            <div class="form-group">
              <label for="keywords">Keywords (separated by ","):</label>
              <input type="text" id="keywords" name="keywords" class="form-control" value="{{keywords}}"/>
            </div>
            <div class="form-group">
              <label for="changes">Changes:</label>
              <input type="text" id="changes" name="changes" class="form-control" value="{{changes}}"/>
            </div>
              <input type="hidden" name="docid" value="{{docid}}"/>
              <input type="hidden" name="docref" value="{{docref}}"/>
            <div class="form-group">
      <label for="upload">Select a file:</label>
              <input type="file" id="upload" name="upload" />
              </div>
            <div class="form-group">
              <label for="sigtext">Signature:</label>
              <textarea class="form-control" name="sigtext" id="sigtext" value="{{sigtext}}"></textarea>
            </div>
          <div class="form-group">
      <label for="signature">Or select a signature file for the file above:</label>
            <input type="file" id="signature" name="signature" />
            </div>
            <div class="checkbox">
    <label>
      <input type="checkbox" name="ccheck"> I certify that I own all rights to this document to upload it for public access on IPFS.
    </label>
  </div>
          <button type="submit" class="btn btn-default">Update</button>
      </form>

      </div>
</div>
    </div> <!-- /container -->


% include('templates/footer.tpl')
  <script>
            $( "#upload" ).addClass( "active" );
        </script>
  </body>
</html>

