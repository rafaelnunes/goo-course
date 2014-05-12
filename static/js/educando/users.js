function UserController($scope){
	$scope.show_profile = function(){
		console.warn('Showing user profile!!!');
		$scope.timesec = new Date();
	};
}