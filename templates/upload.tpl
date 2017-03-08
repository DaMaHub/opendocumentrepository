<!DOCTYPE html>
<html lang="en">
% include('templates/header.tpl', title='Kubrik.io Open Document Proof Of Concept')

  <body>

% include('templates/navbar.tpl')

    <div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="page-header" style="padding-top:40px;">
        <h1>Upload Document</h1>
      </div>
        <div class="row marketing">
        <div class="col-lg-6">
        <p>Here you can upload a document into the repository</p>
        <p>

          <form action="upload" method="post" enctype="multipart/form-data">
            <div class="form-group">
              <label for="category">Category:</label>
              <input type="text" name="category" class="form-control"/>
            </div>
            <div class="form-group">
              <label for="author">Author:</label>
              <input type="text" name="author" class="form-control"/>
            </div>
            <div class="form-group">
              <label for="keywords">Keywords (separated by ","):</label>
              <input type="text" name="keywords" class="form-control"/>
            </div>
            <div class="form-group">
      <label for="upload">Select a file:</label>
              <input type="file" name="upload" />
              </div>

          <div class="form-group">
      <label for="signature">Select a signature file for the file above:</label>
            <input type="file" name="signature" />
            </div>
            <div class="checkbox">
    <label>
      <input type="checkbox" name="ccheck"> I certify that I own all rights to this document to upload it for public access on IPFS.
    </label>
  </div>
          <button type="submit" class="btn btn-default">Start upload</button>
      </form>
        </p>
      </div>
</div>
    </div> <!-- /container -->


% include('templates/footer.tpl')
  <script>
            $( "#upload" ).addClass( "active" );
        </script>
  </body>
</html>

