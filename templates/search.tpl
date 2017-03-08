<!DOCTYPE html>
<html lang="en">
% include('templates/header.tpl', title='Kubrik.io Open Document Proof Of Concept')

  <body>

% include('templates/navbar.tpl')

    <div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="page-header" style="padding-top:40px;">
        <h1>Search Document repository</h1>
      </div>
      <div class="row marketing">
        <div class="col-lg-10">

        <p>This shows an example for a blockchain based open document repository. Please fill in your search terms.</p>
        <p>
        </p>
            <form action="search" method="get">
                <div class="form-group">
              <label for="keywords">Keywords (separated by ","):</label>
              <input type="text" name="keywords" class="form-control"/>
            </div>

          <button type="submit" class="btn btn-default">Start search</button>
      </form>
      </div>

    </div> <!-- /container -->


% include('templates/footer.tpl')
        <script>
            $( "#search" ).addClass( "active" );
        </script>
  </body>
</html>

