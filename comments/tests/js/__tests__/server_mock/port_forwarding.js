const exec = require('child_process').exec;

//#region
/**
 * By passing func which calls $ajax as a callback, we assure that it will be called
 * after port was forwarded. If, not, even if we call forwardPort80To9001 in beforeAll
 * and $ajax function in test, it is very likely that $ajax will be called before
 * ecex function executes these commands.
 */
//#endregion
export function forwardPort80To9001(successCallback) {
    //#region
    /**
     * sudo password (normal user password by default). Password is not shown in
     * shell history (.bash_history) when this script is runned. Just command "node
     * port_forwarding.js" which runs the script.
     */
    //#endregion
    const pass = '123456';

    const commands = [];
    //#region
    /**
     * 1. Because pftcl command requres superuser (root) to run it - it requires
     *    sudo command. So, with this command, we do root login first. We echo our
     *    password and then run sudo -S -i; -i means 'login', and -S means 'read
     *    password from standard input' - this command automatically reads and
     *    'enters' the echoed password to login prompt which is raised by sudo -i.
     *    Now we can execute sudo commands.
     * 2. Bacause we run tests from root directory (~/pyProjects/my_news), that is a
     *    path which will be returned by '.' in 3rd command (./pf_remove.sh). But
     *    this shell script is not located in rood dir, so we navigate to its folder
     *    first (server_mock), and then execute the script in 3rd command. We could
     *    execute the script in one line by:
     *    ./comments/tests/js/__tests__/server_mock/pf_80to9001.sh ,
     *    but it is more readable this way.
     */
    //#endregion
    commands.push(`echo ${pass} | sudo -S -i`);
    commands.push('cd comments/tests/js/__tests__/server_mock');
    commands.push('./pf_80to9001.sh');

    exec(commands.join(' && '), (err, stdout) => {
        if (err) {
            console.log(err);
            return;
        } 
        console.log('*** Successfull port forwarding: 80 -> 9001 ***\n  ', stdout);
        successCallback();
    });
}

export function removePortForwarding(successCallback) {
    const commands = [];
    commands.push('cd comments/tests/js/__tests__/server_mock');
    commands.push('./pf_remove.sh');
    // make sudo logout 
    commands.push('sudo -k');

    exec(commands.join(' && '), (err) => {
        if (err) {
            console.log(err);
            return;
        }
        console.log('*** Port forwarding removed successfully ***');
        successCallback();
    });
}