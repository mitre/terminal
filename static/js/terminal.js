// talk to server
let webSocket = location.hostname+':8765';

// build terminal emulator
let prompt = "~$ ";
let term = new Terminal();
term.setOption('cursorBlink', true);
term.open(document.getElementById('xterminal'));

// run terminal emulator
let input = "";
term.onData(function(data) {
 const code = data.charCodeAt(0);
 if(code === 13) {
     runCommand(input);
     input = "";
 } else if (code === 127) {
     if (input.length > 0) {
         term.write("\b \b");
         input = input.substr(0, input.length - 1);
     }
     return;
 } else if (code < 32) {
     return;
 } else {
     term.write(data);
     input += data;
 }
});

function runCommand(input) {
 let sessionId = $('#session-id option:selected').attr('value');
 let socket = new WebSocket('ws://'+webSocket+'/'+sessionId);
 socket.onopen = function () {
     socket.send(input);
 };
 socket.onmessage = function (s) {
     try {
         let jData = JSON.parse(s.data);
         let lines = jData["response"].split('\n');
         for(let i = 0;i < lines.length;i++){
            term.write("\r\n"+lines[i]);
         }
         prompt = jData["pwd"];
         term.write("\r\n"+prompt+" ");
     } catch(err){
         term.write("\r\n"+'Dead session. Probably. It has been removed.');
         clearTerminal();
         $('#session-id option:selected').remove();
     }
 };
}

// general helpful functions

function displayCommand(){
$('#delivery-command').text(atob(document.getElementById("dcommands").value));
}

function openLocalDuk() {
 document.getElementById("duk-modal").style.display="block";
$('#duk-text').text('Did you know... you can also deploy a new reverse-shell by running an operation using ' +
    'the terminal adversary. Make sure you also use the terminal facts, which contain the location of the ' +
    'TCP socket. You will need to update this value if you are running anywhere but localhost.');
}

function openLocalDuk2() {
 document.getElementById("duk-modal").style.display="block";
$('#duk-text').text('Did you know... there are a handful of special commands you can run in a session. ' +
    'Check the documentation for a full list.');
}

function removeSection(identifier){
 $('#'+identifier).hide();
}

// ability filter options

let ABILITIES = [];
function getAbilities() {
 function getAbilitiesCallback(data){
    $('#tactic-filter').empty().append("<option disabled='disabled' selected>Choose a tactic</option>");
     ABILITIES = [];
     let found = [];
     data.abilities.forEach(function(ability) {
         ABILITIES.push(ability);
         if(!found.includes(ability.tactic)) {
             $('#tactic-filter').append('<option value="'+ability.tactic+'">'+ability.tactic+'</option>');
             found.push(ability.tactic);
         }
     });
 }
 restRequest('POST', {"paw": $('#session-id option:selected').data('paw')}, getAbilitiesCallback, '/ability');
}
function filterTechniques() {
 let found = [];
 $('#technique-filter').empty().append("<option disabled='disabled' selected>Choose a technique</option>");
 ABILITIES.forEach(function(ability){
     if(ability.tactic === $('#tactic-filter').val() && !found.includes(ability.technique_id)) {
         $('#technique-filter').append('<option value="'+ability.technique_id+'">'+ability.technique_id+' | '+ability.technique_name+'</option>');
         found.push(ability.technique_id);
     }
 });
}
function filterProcedures() {
 $('#procedure-filter').empty().append("<option disabled='disabled' selected>Choose a procedure</option>");
 ABILITIES.forEach(function(ability){
     if(ability.tactic === $('#tactic-filter').val() && ability.technique_id === $('#technique-filter').val()) {
         $('#procedure-filter').append('<option value="'+ability.ability_id+'">'+ability.name+'</option>');
     }
 });
}
function showProcedure() {
 ABILITIES.forEach(function(ability){
     if(ability.ability_id === $('#procedure-filter').val()) {
         term.write(atob(ability.test));
         input = atob(ability.test);
         return;
     }
 });
}

function clearTerminal(){
    input = "";
    prompt = '~$ ';
    term.write("\r\n"+prompt+" ");
}