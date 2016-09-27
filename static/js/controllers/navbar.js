/* globals Auth0Lock: false */
'use strict';

// login and other top-screen controls
app.controller('NavbarCtrl', ['$scope', '$http', function($scope, $http) {

    $http({method: 'GET', url: '/api/user'}).then(function(user) {
        $scope.user = user.data;
    });

    $scope.showLogin = function _a_showLogin() {
        var lock = new Auth0Lock(
                $scope.preload.auth0Public,
                'nomsbook.auth0.com');
        lock.show({
            // This is the smallest possible transparent GIF image; in effect
            // hiding the icon
            icon: "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==",
            callbackURL: $scope.preload.apparentURL + '/api/sso',
            responseType: 'code',
            authParams: { scope: 'openid profile' }
        });
    };

}]);

