/**
 * 1. This method creates a server that serve files from server_mock folder on
 *    localhost:9001
 * 2. Now to create mocked response with url just localhost:9001, we create
 *    GET.mock file inside server_mock folder. The file name is
 *    <HTTP_METHOD>.mock -> name of the file is http method we want to use
 *    (uppercase), and extension is .mock
 * 3. Creating urls: for example we want to mock response for POST request to
 *    url = /comments/load-more-comments/. for this, we will create comments
 *    folder inside server_mock folder, and then load-more-comments folder
 *    inside comments folder. And then we will create POST.mock file inside
 *    load-more-comments. Now we open browser and go to
 *    localhost:9001/comments/load-more-comments/, and we get our mocked
 *    response.
 * 4. In .mock files, we can define everything like in real response:
 *    content-type, HTTP status code, content of the response (body), and
 *    whatever we want (see in documentation for more):
 *     https://tech.namshi.io/blog/2014/06/13/mockserver-effortless-api-mocking-library-in-node-js/
 *    https://github.com/namshi/mockserver 
 * 5. Here i wrapped everithing in a function so i can export it and use in tests
 */ 

const http    =  require('http');
const mockserver  =  require('mockserver');
const path = require('path');

//#region
/**
 * path.resolve('.') returns path from which node was started. When we run
 * "node_modules/.bin/jest load_comments.test.js" command, we run it from
 * project directory: 
 *      (my-news-env) luka@MacBook-Pro ~/pyProjects/my_news (master) $ node_modules/.bin/jest load_comments.test.js 
 * So, when we run our test like above, path.resolve('.') returns
 * '/Users/luka/pyProjects/my_news'. Now, our mockserver has to serve from
 * server_mock directory - so we define that path with:
 * path.resolve('./comments/tests/js/__tests__/server_mock'); 
 * which returns => /Users/luka/pyProjects/my_news/comments/tests/js/__tests__/server_mock, 
 * and mockserver works in tests
 */
//#endregion
const _path = path.resolve('./comments/tests/js/__tests__/server_mock');
const server = http.createServer(mockserver(_path));

export function runMockServer(){
    server.listen(9001);
}

export function stopMockServer(){
    server.close();
}