'use strict'; 

// login and other top-screen controls
app.controller('NavbarCtrl', ['$scope', '$http', function($scope, $http) {

    $http({method: 'GET', url: '/api/user'}).then(function(user) {
        $scope.user = user.data; 
    }); 
  
    $scope.showLogin = function _a_showLogin() {
        var lock = new Auth0Lock(
                'zhcnJuMWPCY2XMRH2afRNST7tpGUE9Hp', // FIXME move to config code
                'nomsbook.auth0.com');
        lock.show({
            callbackURL: 'https://ee180441.ngrok.io/api/sso',
            responseType: 'code',
            authParams: { scope: 'openid profile' }
        });
    };

}]); 

