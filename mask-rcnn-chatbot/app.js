//Imports
var builder = require('botbuilder'); //Microsoft BotFramework SDK for building chatbots
var express = require('express');
var Promise = require('bluebird');
var path = require('path');
var bodyParser = require('body-parser');
var request = require('request-promise').defaults({ encoding: null });
require('dotenv').load();

const app = express();
var router = express.Router();

record = "";

//The ChatConnector enables communication between bot and user via various channels
//such as Web, Slack, Facebook, Skype, etc.
var connector = new builder.ChatConnector({
    appId: process.env.APP_ID,
    appPassword: process.env.APP_PASSWORD
});

app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.json({ limit: '100mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '100mb' }));

/********************
     WEB HOSTING
*********************/
router.get('/', function (req, res) {
    res.sendFile(path.join(__dirname, 'public') + "/" + "index.html");

    console.log("get / called")
});

app.get('/index.html', function (req, res) {
    console.log("get /index.html called")
    res.sendFile(path.join(__dirname, 'public') + "/" + "index.html");
});

app.listen(process.env.port || process.env.PORT || 3978, function () {
    console.log('%s started', app.name);
});

app.post('/api/messages', connector.listen());

//Create a new 'bot' variable that is type UniversalBot with MemoryBotStorage
//MemoryBotStorage saves the session state
var inMemoryStorage = new builder.MemoryBotStorage();
var bot = new builder.UniversalBot(connector, function (session) {
    var msg = session.message;
    if (msg.attachments.length) {   
        // Message with attachment, proceed to download it.
        // Skype & MS Teams attachment URLs are secured by a JwtToken, so we need to pass the token from our bot.
        var attachment = msg.attachments[0];
        var fileDownload = checkRequiresToken(msg)
            ? requestWithToken(attachment.contentUrl)
            : request(attachment.contentUrl);
        fileDownload.then(
            postData(fileDownload, session, function(response){
                session.send("image prediction completed");
                var msg = new builder.Message(session);
                msg.textLocale("en-us");
                var contentType = 'image/png';
                msg.text("Reading image...");
                msg.addAttachment({
                    contentUrl: response.toString('utf8'),
                    contentType: contentType
                });
                session.send(msg);
            }))
    } else {
        // No attachments were sent
        var reply = 'Sorry, I don\'t understand';
        session.endDialog(reply);
    }
}).set('storage', inMemoryStorage); // Register in memory storage

// Request file with Authentication Header
var requestWithToken = function (url) {
    return obtainToken().then(function (token) {
        return request({
            url: url,
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/octet-stream'
            }
        });
    });
};

// Promise for obtaining JWT Token (requested once)
var obtainToken = Promise.promisify(connector.getAccessToken.bind(connector));
var checkRequiresToken = function (message) {
    return message.source === 'skype' || message.source === 'msteams';
};

bot.use({
    botbuilder: function (session, next) {
        session.sendTyping();
        session.delay(500);
        next();
    }
});

function postData(data, session, cb){
    request.post({
  	    url: 'http://localhost:5000/',
        body: data
	}, function(error, response, body){
        console.log(response.body);
        session.send({
            text: 'Is this your formula?',
            attachments: [{
                contentUrl: "data:image/png;base64," + response.body,
                contentType: "image/png",
                name: "datauri"
            }]
        })
    });
}

//Send greeting when conversation is opened
bot.on('conversationUpdate', function (message) {
    if (message.membersAdded) {
        message.membersAdded.forEach(function (identity) {
            if (identity.id === message.address.bot.id) {
                bot.beginDialog(message.address, 'Greeting');
            }
        });
    }
});

var fs = require('fs');

// function to encode file data to base64 encoded string
function base64_encode(file) {
    // read binary data
    var bitmap = fs.readFileSync(file);
    // convert binary data to base64 encoded string
    return new Buffer(bitmap).toString('base64');
}

// bot.dialog('LaTex', [
//     function (session) {
//         i = 0;
//         //reminder we can store variables in the session - useful for longer sessions
//         session.endDialog('Submit a formula!');
//     }, function (session, results) {
//         session.dialogData.wordInput = results.response
//         record += session.dialogData.wordInput;

//         request.post({
//             url: 'http://127.0.0.1:5000/', // flask server URL - may be //localhost:5500 ?
//             body: record
//     }, function (r1, r2) {
//         response_value = r2.body;
//         split_char = '///'
//         if (response_value.indexOf(split_char) > -1) {
//             outstring = 'Is one of these your formula:\n';
//             // response_value = response_value.split_char(split_char);
//             // for (i = 0; i< response_value.length; i++) {
//             //     outstring += response_value[i] + '\n';
//             // }
//             outstring += response_value;
//             outstring += '?';

//             session.endDialog(outstring);
//         }

//         session.endDialog('Is your formula: ' + response_value + '?');
//         });
//     }
// ]).triggerAction({
//     //Matches regex string of 'hi's and 'hello's
//     matches:  [/^botlatex*$|/i],
// });

//Greeting dialog
bot.dialog('Greeting', function(session){
    session.endDialog('Hi! Send me a picture of your formula and I\'ll give you the LaTex code for it!');
}).triggerAction({
    //Matches regex string of 'hi's and 'hello's
    matches: [/^hey*$|^hello*$|^sup*$|^hi*$|^latex*$/i],
});

var recognizer = new builder.LuisRecognizer("https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/dde153e8-ea41-435a-84e6-7391513b6b1d?subscription-key=7f73dab185564f07a2d8b081f510edea&verbose=true&timezoneOffset=0&q=").onEnabled(function(context, callback) { var enabled = context.dialogStack().length == 0; callback(null, enabled)});
bot.recognizer(recognizer);

bot.dialog('Math', function(session, args){
    session.endDialog('Hello.');
    var number = builder.EntityRecognizer.findEntity(args.entities, 'builtin.number')
}).triggerAction({
    //Matches regex string of 'hi's and 'hello's
    matches: "MathEquation"
});
