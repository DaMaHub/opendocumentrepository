<!DOCTYPE html>
<html lang="en">
% include('templates/header.tpl', title='Kubrik.io Open Document Proof Of Concept')

  <body>

% include('templates/navbar.tpl')

    <div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="page-header" style="padding-top:40px;">
        <h1>Browse Published Documents</h1>
      </div>
      <div class="row">
        <div class="col-lg-10">

        <p>
        This is a list of all documents in this demo repository so far.
        </p>

      </div>
          <div class="row">
        <div class="col-lg-10">

        {{!data}}

      </div>
    </div>
    </div> <!-- /container -->


% include('templates/footer.tpl')
    <script>
            $( "#browse" ).addClass( "active" );
        </script>
  </body>
</html>

