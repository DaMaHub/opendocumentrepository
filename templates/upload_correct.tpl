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
      <div class="row">
        <div class="col-lg-10">

        <p>
        File uploaded correctly. You will be redirected to the upload page in 5 seconds.
        </p>
      </div>
        </div>
    </div> <!-- /container -->


% include('templates/footer.tpl')
  <script type="text/JavaScript">
      setTimeout("location.href = 'upload';",5000);
 </script>
  </body>
</html>

