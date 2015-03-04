(function() {
    $('#register-panel').hide();
    $('#login-panel').show();
    $('#register-btn').on('click', function() {
        $('#login-panel').hide();
        $('#register-panel').show();
    });
    $('#login-btn').on('click', function() {
        $('#register-panel').hide();
        $('#login-panel').show();
    });
}());
