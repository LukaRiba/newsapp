// this is setup for debugging js code which uses ES6 - as debugger runs files through node, error will be thrown
// because of unsuported syntax - import or * or something else. So, we install @babel/register plugin, then
// add this lines here - with second holding the path of file we want to run. Now, we run it with:
//  $ node register.js  -> this command will run our create_comment.test.js and now the syntax will be recognized.
// In launch.json, we set "program": "${workspaceFolder}/register.js" in our configuration - so it runs this file which wraps
// the test file we want to run.
require("@babel/register");
require("./comments/static/comments/js/__tests__/create_comment.test.js");