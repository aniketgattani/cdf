var app = angular.module('chat', ['ngSanitize'])

Pusher.logToConsole = false;

var pusher = new Pusher('00f94d2692aca226deee', {
    cluster: 'ap2',
    encrypted: true
});

var channel = pusher.subscribe('chatterJi');

app.run(function($rootScope, $http) {
    $http.get('/getUsers').then(function(results) {
        console.log(results.data.online)
        $rootScope.online = results.data.online
        setTimeout(function() {
            document.getElementsByClassName("uk-online-box")[0].click()
        }, 0)
    })
    $rootScope.userName = uname
})
app.controller('messsagesController', function($scope, $rootScope, $http) {
    setTimeout(function() {
        var messageBody = document.querySelector('#uk-messages-box')
        messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight
    }, 0)
})

app.controller('composeController', function($scope, $rootScope, $http) {
    $scope.message = ""
    $scope.emojisSuggested = []
    $http.get('/emoji').then(function(results) {
        var messages =  results.data.data
        for (var i = 0; i < messages.length; i++) {
            messages[i].emoji = emojione.shortnameToImage(messages[i].name)
        }
        $scope.emojis = messages
    })

    channel.bind('newMsg', function(response) {
        response['message'] = emojione.shortnameToImage(response['message'])
        var data = response
        var currentUser = document.getElementsByClassName("active")[0].id
        console.log(currentUser)
        console.log(uid)
        console.log(response)
        if (response['from'] == currentUser && response['to'] == uid) {
            data['me'] = false
            $rootScope.messages.push(data)
            console.log(data)
            setTimeout(function() {
                var messageBody = document.querySelector('#uk-messages-box')
                messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight
                $scope.message = ""
                $scope.$apply()
                if (document.getElementById("emojiContainer").getAttribute("hidden") == "") {
                } else {
                    document.getElementById("emoji-button").click()
                }
            }, 0)
        } else if (response['to'] == currentUser && response['from'] == uid) {
            data['me'] = true
            $rootScope.messages.push(data)
            console.log(data)
            setTimeout(function() {
                var messageBody = document.querySelector('#uk-messages-box')
                messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight
                $scope.message = ""
                $scope.$apply()
                if (document.getElementById("emojiContainer").getAttribute("hidden") == "") {
                } else {
                    document.getElementById("emoji-button").click()
                }
            }, 0)    
        } else if (response['to'] == uid) {
            document.getElementById(response['from']).className+=" newMsgRcd"
            document.getElementById(response['from']).innerHTML+="<span class='uk-badge uk-text-primary customBadge'>New</span>"
        }
    });

    $scope.getEmoji = function($event) {
        if ($scope.message == "") {
            $scope.emojisSuggested = []
            if (document.getElementById("emojiContainer").getAttribute("hidden") == "") {
            } else {
                document.getElementById("emoji-button").click()
            }
        }
        if ($event.keyCode == 32) {
            $scope.emojisSuggested = []
            var message = $scope.message
            var dataObj = {"message": message}
            $http({
                url: '/suggest',
                method: "POST",
                data: dataObj,
                dataType:'json',
            }).then(function(response) {
                console.log(response.data.emoji)
                for (var i = 0; i < response.data.emoji.length; i++) {
                    var data = response.data.emoji[i] 
                    var emoji = emojione.shortnameToImage(response.data.emoji[i])
                    $scope.emojisSuggested.push({
                        name: data,
                        emoji: emoji
                    })    
                }
                setTimeout(function() {
                    if (document.getElementById("emojiContainer").getAttribute("hidden") == "") {
                        document.getElementById("emoji-button").click()
                    }
                }, 0)
            }, function() {
                console.log("oops")
            }) 
        }
    }

    $scope.addEmoji = function(emoji) {
        console.log(emoji)
        $scope.message += emoji
    }

    $scope.sendMessage = function() {
        var toid = document.getElementsByClassName('active')[0].id
        var dataObj = {"message": $scope.message, "msg_to": toid, "msg_from": 4}
        $http({
            url: '/message',
            method: "POST",
            data: dataObj,
            dataType:'json',
        }).then(function(response) {
        }, function() {
            console.log("oops")
        }) 
    }
})

app.controller('onlineController', function($scope, $rootScope, $http) {
    $scope.userChat = function() {
        var userObj = this.m
        var thisUser = document.getElementById(userObj.id)
        if (thisUser.childNodes.length >= 2) {
            thisUser.removeChild(thisUser.childNodes[1])  
        } 
        var active = document.getElementsByClassName("active")[0]
        if (active) {
            document.getElementsByClassName("active")[0].className = document.getElementsByClassName("active")[0].className.replace(" active", "")
        }
        document.getElementById(userObj.id).className+=" active"
        var userName = document.getElementById("userName")
        if (userName.innerHTML.trim() != userObj.name) {
            userName.innerHTML = userObj.name
            $rootScope.messages = [
                {
                    "message": "We're loading",
                    "me": false
                },
                {
                    "message": "Please hold on...",
                    "me": false
                },
                {
                    "message": "It's almost there",
                    "me": false
                }
            ]
            var toid = document.getElementsByClassName('active')[0].id
            $http.get('/data/?id=' + toid).then(function(results) {
                var messages = results.data.messages
                for (var i = 0; i < messages.length; i++) {
                    messages[i].message = emojione.shortnameToImage(messages[i].message)
                }
                $rootScope.messages = messages
                setTimeout(function() {
                    var messageBody = document.querySelector('#uk-messages-box')
                    messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight
                }, 0)
            })
        }
    }
})