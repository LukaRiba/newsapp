/**
Forward Port 80 Mac pfctl Port Forwarding:
     echo "rdr pass inet proto tcp from any to any port 80 -> 127.0.0.1 port 9001 " | sudo pfctl -ef -
Remove Port Forwarding:
     sudo pfctl -F all -f /etc/pf.conf
Display Your Current Port Forwarding Rules:
     sudo pfctl -s nat
 */

const { exec } = require('child_process');

// sudo password (normal user password by default). Password is not shown in
// shell history (.bash_history) when this script is runned. Just command "node
// port_forwarding.js" which runs the script.
const pass = '123456';

// Because pftcl command requres superuser (root) to run it - it requires sudo command.
// So, with this command, we do root login first. We echo our password and then run
// sudo -S -i; -i means 'login', and -S means 'read password from standard input' - this command automatically
// reads and 'enters' the password which is echoed. Now we can execute sudo commands.
exec(`echo ${pass} | sudo -S -i`, (err, stdout, stderr) => {
    if (err) {
        return;
    } 
    console.log('Loggeed in successfully!');
});



exec('echo "rdr pass inet proto tcp from any to any port 80 -> 127.0.0.1 port 9001 " | sudo pfctl -ef -', (err, stdout, stderr) => {
    if (err) {
        return;
    } 
    console.log('Successfull port forwarding: 80 -> 9001');
});

// exec('sudo -k', (err, stdout, stderr) => {
//     if (err) {
//         return;
//     } 
// });



// setTimeout( () => { cmd.stdin.write('123456\n'); }, 2000)

// setTimeout(() => {
//     exec('sudo pfctl -s nat', (err, stdout, stderr) => {
//         if (err) {
//           // node couldn't execute the command
//           return;
//         }
      
//         // the *entire* stdout and stderr (buffered)
//         console.log(`stdout:\n${stdout}`);
//         console.log(`stderr:\n${stderr}`);
//       });
// }, 2000);

// setTimeout(() => {
//     exec('sudo pfctl -F all -f /etc/pf.conf', (err, stdout, stderr) => {
//         if (err) {
//           // node couldn't execute the command
//           return;
//         }
      
//         // the *entire* stdout and stderr (buffered)
//         console.log(`stdout:\n${stdout}`);
//         console.log(`stderr:\n${stderr}`);
//         console.log('Port forwarding removed successfully');
//       });
// }, 4000);
