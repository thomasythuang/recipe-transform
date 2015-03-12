var app = angular.module('recipesApp', []);

app.controller('mainController', function ($scope, $http){
  
  console.log('loaded');

  $scope.step = 1;
  $scope.recipe = {};
  $scope.original = {};
  $scope.parsing = false;	// Parsing in progress?
  $scope.transforming = false;	// Transforming in progress?

  $scope.test = function(){
  	console.log($scope.transform);
  }

  $scope.parse = function(){
  	$scope.parsing = true;

  	//$http.post('/parse', $scope.url)
  	$http.get('https://api.myjson.com/bins/34luf')
  		.success(function(data){
  			console.log(data);
  			$scope.recipe = data;
  			$scope.original = $scope.recipe;
  			$scope.step = 2;
  		})
  		.error(function(data, status, headers, config){
  			console.log(status);
  			alert("The URL was invalid, try another");
  		}); 

		$scope.parsing = false;
  }

  $scope.transformRecipe = function(){
  	$scope.transforming = true;

  	//$http.post('/transform/' + $scope.transform. $scope.recipe)
  	$http.get('https://api.myjson.com/bins/vdgn')
  		.success(function(data){
  			console.log(data);
  			$scope.recipe = data;
  		})
  		.error(function(data, status, headers, config){
  			console.log(status);
  			console.log("The transform failed");
  		});

  	$scope.transforming = false;
  }

  $scope.goToStep = function(i){
  	$scope.step = i
  }

  $scope.revert = function(){
  	$scope.recipe = $scope.original;
  }

  $scope.desc = function(d){
  	if (d == "none"){
  		return;
  	}else{
  		return d;
  	}
  }
});