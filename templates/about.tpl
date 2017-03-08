<!DOCTYPE html>
<html lang="en">
% include('templates/header.tpl', title='Kubrik.io Open Document Proof Of Concept')

  <body>

% include('templates/navbar.tpl')

    <div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="page-header" style="padding-top:40px;">
        <h1>About</h1>
      </div>
      <div class="row marketing">
        <div class="col-lg-6">

        <p>
        We believe that transparent organisations should have a simple way to publish documents
            in a transparent and persistent way on the web.
        </p>
      </div>
        </div>
    </div> <!-- /container -->


% include('templates/footer.tpl')
  <script>
            $( "#about" ).addClass( "active" );
        </script>
  </body>
</html>

