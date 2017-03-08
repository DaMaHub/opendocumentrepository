<!DOCTYPE html>
<html lang="en">
% include('templates/header.tpl', title='Kubrik.io Open Document Proof Of Concept')

  <body>

% include('templates/navbar.tpl')

    <div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="page-header" style="padding-top:40px;">
        <h1>Bootstrapping from Blockchain</h1>
      </div>
      <div class="row">
        <div    class="col-lg-10">
            <p>
        Deleting old search database... done.
        </p>
            <p>
        Reading data from blockchain... done.
        </p>

        <p>
        The following documents were added from the blockchain
        </p>

      </div>
          </div>
          <div class="row">
        <div class="col-lg-10">

        {{!data}}

      </div>
    </div>
    </div> <!-- /container -->


% include('templates/footer.tpl')
    <script>
            $( "#bootstrap" ).addClass( "active" );
        </script>
  </body>
</html>

